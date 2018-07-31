#!/usr/bin/env python3

import markdown
from os.path import expanduser

def mimedown(markdown_content):
    with open(expanduser('~/.markdown-email/email.css')) as f:
        css = f.read()
    html_content = markdown.markdown(
        markdown_content,
        ['extra', 'codehilite', 'tables'])
    return '''
--<<alternative>>-{
--[[text/plain]]
    %s
--[[text/html]]
<style type="text/css">%s</style>
<div class="container">
    %s
</div>
--}-<<alternative>>
''' % (markdown_content, css, html_content)


if __name__ == "__main__":
    import sys
    mardkwon_content = sys.stdin.read()
    result = mimedown(mardkwon_content)
    sys.stdout.write(result)
