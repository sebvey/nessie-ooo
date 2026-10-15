"""Minimal Nessie v2 client — the 'git' control plane: branch / merge / delete / list.

Kept intentionally tiny and dependency-light (just requests) so it reads clearly in a demo.
"""

from __future__ import annotations

from dataclasses import dataclass

import requests

from .settings import settings


class NessieError(RuntimeError):
    pass


@dataclass
class MergeResult:
    successful: bool
    applied: bool
    target_hash: str
    raw: dict


class Nessie:
    def __init__(self, api_uri: str | None = None):
        self.base = (api_uri or settings.nessie_api_uri).rstrip("/")

    # --- helpers ---
    def _get(self, path: str) -> dict:
        r = requests.get(f"{self.base}{path}")
        if not r.ok:
            raise NessieError(f"GET {path} -> {r.status_code}: {r.text}")
        return r.json()

    def ref_hash(self, ref: str) -> str:
        return self._get(f"/trees/{ref}")["reference"]["hash"]

    def no_ancestor_hash(self) -> str:
        """The pristine 'beginning of time' hash a brand-new branch points at (no commits yet)."""
        return self._get("/config")["noAncestorHash"]

    def list_branches(self) -> list[dict]:
        return self._get("/trees")["references"]

    def branch_exists(self, name: str) -> bool:
        r = requests.get(f"{self.base}/trees/{name}")
        return r.status_code == 200

    # --- mutations ---
    def create_branch(self, name: str, from_ref: str = "main") -> str:
        """Create `name` pointing at the tip of `from_ref`. Returns the new branch hash."""
        src_hash = self.ref_hash(from_ref)
        body = {"type": "BRANCH", "name": from_ref, "hash": src_hash}
        r = requests.post(f"{self.base}/trees?name={name}&type=BRANCH", json=body)
        if not r.ok:
            raise NessieError(f"create_branch {name} -> {r.status_code}: {r.text}")
        return r.json()["reference"]["hash"]

    def delete_branch(self, name: str) -> None:
        h = self.ref_hash(name)
        r = requests.delete(f"{self.base}/trees/{name}@{h}")
        if not r.ok:
            raise NessieError(f"delete_branch {name} -> {r.status_code}: {r.text}")

    def create_tag(self, name: str, from_ref: str = "main") -> str:
        """Create an immutable TAG pointing at the tip of `from_ref`. Nessie requires the
        name to start with a letter (a pure YYYYMMDD is rejected)."""
        src_hash = self.ref_hash(from_ref)
        body = {"type": "BRANCH", "name": from_ref, "hash": src_hash}  # the source reference
        r = requests.post(f"{self.base}/trees?name={name}&type=TAG", json=body)
        if not r.ok:
            raise NessieError(f"create_tag {name} -> {r.status_code}: {r.text}")
        return r.json()["reference"]["hash"]

    def delete_tag(self, name: str) -> None:
        h = self.ref_hash(name)
        r = requests.delete(f"{self.base}/trees/{name}@{h}")
        if not r.ok:
            raise NessieError(f"delete_tag {name} -> {r.status_code}: {r.text}")

    def merge(self, from_branch: str, into: str = "main") -> MergeResult:
        """Merge `from_branch` into `into`. Atomic on the Nessie side."""
        from_hash = self.ref_hash(from_branch)
        into_hash = self.ref_hash(into)
        body = {"fromRefName": from_branch, "fromHash": from_hash}
        r = requests.post(f"{self.base}/trees/{into}@{into_hash}/history/merge", json=body)
        if not r.ok:
            raise NessieError(f"merge {from_branch}->{into} -> {r.status_code}: {r.text}")
        j = r.json()
        return MergeResult(
            successful=j.get("wasSuccessful", False),
            applied=j.get("wasApplied", False),
            target_hash=j.get("resultantTargetHash", ""),
            raw=j,
        )

    def entries(self, ref: str) -> list[dict]:
        """Contents (namespaces, tables) of `ref`, e.g. {"type": "NAMESPACE", "name": {"elements": ["raw"]}}."""
        return self._get(f"/trees/{ref}/entries")["entries"]

    def log(self, ref: str, limit: int = 10) -> list[dict]:
        j = self._get(f"/trees/{ref}/history?maxRecords={limit}")
        return j.get("logEntries", [])
