"""Validate the bounded Docker upgrade against the previous GBK CGI source."""
from pathlib import Path
import subprocess
import tempfile
import unittest

class NewsUpgradeTest(unittest.TestCase):
    def test_old_crlf_and_lf_sources_preserve_custom_changes_and_upgrade_once(self):
        root = Path(__file__).resolve().parents[2]
        program = (root / 'docker-entrypoint.sh').read_text().split("<<'NEWS_VIEW_PATCH'\n", 1)[1].split('\nNEWS_VIEW_PATCH', 1)[0]
        # Reconstruct precisely the old parsing block without relying on Git HEAD.
        fixed = (root / 'cgi-bin/view.cgi').read_bytes().replace(b'\r\n', b'\n')
        start = fixed.index(b'return resp.arrayBuffer();')
        end = fixed.index(b"html = '<DIV class=ts>", start)
        old_block = br'''return resp.text();
}).then(function(html){
html = html.replace(/^[\s\S]*<body[^>]*>/i, "").replace(/<\/body>[\s\S]*$/i, "");
html = html.replace(/<script[\s\S]*?<\/script>/ig, "");
if (html.replace(/\s/g, "") == ""){
'''
        for newline in [b'\n', b'\r\n']:
            with self.subTest(newline=newline), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'view.cgi'
                extra = b'\n# site-local custom comment\n'
                path.write_bytes((fixed[:start] + old_block + fixed[end:] + extra).replace(b'\n', newline))
                expected = (fixed + extra).replace(b'\n', newline)
                for _ in range(2):
                    subprocess.run(['python3', '-', str(path), str(root / 'cgi-bin/view.cgi')], input=program.encode(), check=True)
                    self.assertEqual(path.read_bytes(), expected)

    def test_news_ubb_helper_is_added_once_to_previous_installation(self):
        root = Path(__file__).resolve().parents[2]
        program = (root / 'docker-entrypoint.sh').read_text().split("<<'NEWS_VIEW_PATCH'\n", 1)[1].split('\nNEWS_VIEW_PATCH', 1)[0]
        fixed = (root / 'cgi-bin/view.cgi').read_bytes()
        old = fixed.split(b'# LEOBBS_NEWS_UBB_COMPAT:',1)[0].replace(br'&news_lbcode(\$post);',br'&lbcode(\$post);')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'view.cgi'; path.write_bytes(old)
            subprocess.run(['python3','-',str(path),str(root/'cgi-bin/view.cgi')],input=program.encode(),check=True)
            patched = path.read_bytes()
            self.assertEqual(patched.count(b'# LEOBBS_NEWS_UBB_COMPAT:'),1)
            self.assertEqual(patched.count(br'&news_lbcode(\$post);'),2)
            subprocess.run(['python3','-',str(path),str(root/'cgi-bin/view.cgi')],input=program.encode(),check=True)
            self.assertEqual(path.read_bytes(),patched)

if __name__ == '__main__': unittest.main()
