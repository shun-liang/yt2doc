# {{ title }}

{{ video_url }}

{% if add_table_of_contents %}
### Table of contents
{% for chapter in chapters %}
- ({{ chapter.start_h_m_s }}) {{ chapter.title }}
{% endfor %}

{% endif %}
{% for chapter in chapters %}
## {{ chapter.title }} {{ '{' }}{{ chapter.custom_id }}{{ '}' }}

{% for paragraph in chapter.paragraphs %}
{% if to_timestamp_paragraphs %}({{ paragraph.start_h_m_s }}) {% endif %}{{ paragraph.text }}
{% if not loop.last %}

{% endif %}
{% endfor %}
{% endfor %}