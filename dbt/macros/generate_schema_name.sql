{#- A model's custom schema is used as is (`marts`), not prefixed with the target's (`main_marts`):
    the Iceberg namespaces are fixed, created by bootstrap on main. -#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {{ custom_schema_name if custom_schema_name is not none else target.schema }}
{%- endmacro %}
