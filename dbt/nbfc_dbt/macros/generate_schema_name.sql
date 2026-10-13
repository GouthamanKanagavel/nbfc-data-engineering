{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if node.name.startswith('stg_qa_') -%}
        QA_STAGING
    {%- elif node.name.startswith('int_qa_') -%}
        QA_INTERMEDIATE
    {%- elif node.name == 'fact_loan_qa' -%}
        QA_ANALYTICS
    {%- elif custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ default_schema }}_{{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
