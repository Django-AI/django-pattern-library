from pattern_library.utils import is_pattern_library_context, get_pattern_config, render_pattern


def override_tag(register, name):
    """
    An utility that helps you override original tags for use in your pattern library.

    Accepts the register argument which should be an instance of django.template.Library.
    """

    original_tag = register.tags[name]

    @register.tag(name=name)
    def tag_func(parser, token):
        original_node = original_tag(parser, token)
        original_node_render = original_node.render

        def node_render(context):
            if is_pattern_library_context(context):
                # Load pattern's config
                pattern_config = get_pattern_config(parser.origin.template_name)

                # Extract values for lookup from the token
                bits = token.split_contents()
                tag_name = bits[0]
                arguments = ' '.join(bits[1:]).strip()

                # Get config for a specific tag
                tag_config = pattern_config.get('tags', {}).get(tag_name, {})
                if tag_config:
                    # Get config for specific arguments
                    tag_config = tag_config.get(arguments, {})

                    # Render a raw string, if defined
                    raw_string = tag_config.get('raw')
                    if raw_string:
                        return raw_string

                    # Render pattern if defined
                    template_name = tag_config.get('template_name')
                    if template_name:
                        request = context.get('request')
                        return render_pattern(request, template_name)

            return original_node_render(context)

        original_node.render = node_render

        return original_node

    return tag_func
