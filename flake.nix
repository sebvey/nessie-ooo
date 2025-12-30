{
  description = "Dev shell for Nessie + Iceberg (Java only)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSystem = f: builtins.listToAttrs (map (system: { name = system; value = f system; }) systems);
    in {
      devShells = forEachSystem (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in {
          default = pkgs.mkShell {
            packages = [
              pkgs.openjdk21_headless
            ];
            shellHook = ''
              export JAVA_HOME=${pkgs.openjdk21_headless}
              export PATH=$JAVA_HOME/bin:$PATH
              echo "Nix dev shell: JAVA_HOME=$JAVA_HOME"
            '';
          };
        });
    };
}
