"""Exercise news compatibility through the actual legacy UBB parser, no post writes."""
import subprocess
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PROGRAM = r'''
require "code.cgi";
local $/;
open(my $source, '<', $ARGV[0]) or die $!;
my $view = <$source>;
$view =~ /(\# LEOBBS_NEWS_UBB_COMPAT:.*?\# END_LEOBBS_NEWS_UBB_COMPAT)/s or die "missing helper";
eval $1; die $@ if $@;
$hidejf = "yes"; $viewhide = 0;
my $text = <STDIN>;
news_lbcode(\$text);
print $text;
'''
class NewsUbbTest(unittest.TestCase):
    def render(self, body):
        return subprocess.check_output(['perl', '-I', str(ROOT/'cgi-bin'), '-e', PROGRAM, str(ROOT/'cgi-bin/view.cgi')],input=body.encode('gbk')).decode('gbk')

    def test_paragraphs_and_paired_breaks(self):
        for body in ['<p>第一段</p><p>第二段[br][/br]换行</p>', '&lt;p&gt;第一段&lt;/p&gt;&lt;p&gt;第二段[BR][/BR]换行&lt;/p&gt;']:
            self.assertEqual(self.render(body),'第一段<br><br>第二段<br>换行')
        self.assertEqual(self.render('a[br]b&lt;br /&gt;c'), 'a<br>b<br>c')

    def test_code_is_literal_and_real_line_breaks_remain(self):
        rendered = self.render('[code]&lt;p&gt;[br][/br]<br>[b]原样[/b][/code]')
        self.assertIn('<code>&lt;p&gt;&#91;br&#93;&#91;/br&#93;<br>&#91;b&#93;原样&#91;/b&#93;</code>',rendered)
        self.assertIn('&lt;p&gt;', self.render('[code=html]<p>[/code]'))

    def test_disabled_ubb_hidden_content_and_html_attributes(self):
        body = '[DISABLELBCODE]&lt;p&gt;text&lt;/p&gt;[br][/br]'
        self.assertEqual(self.render(body),body.replace('[DISABLELBCODE]',''))
        self.assertNotIn('secret-text', self.render('[hide]&lt;p&gt;secret-text&lt;/p&gt;[/hide]'))
        self.assertIn('&lt;p &#111;nclick=',self.render('&lt;p onclick=alert(1)&gt;literal&lt;/p&gt;'))
        self.assertNotIn('<script>', self.render('&lt;script&gt;alert(1)&lt;/script&gt;'))

if __name__=='__main__': unittest.main()
