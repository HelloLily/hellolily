{% load messages %}

{# Generate notifications based on messages middleware #}
{% if messages %}
$(function($){
    {% for message in messages|unique_messages %}
    toastr['{{ message.tags }}']("{{ message.message|safe }}")
    {% endfor %}
});
{% endif %}
