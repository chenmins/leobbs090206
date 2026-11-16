#!/usr/bin/perl
# Private worker, never exposed as a CGI URL. stdout is a single JSON result;
# ordinary legacy HTML is discarded. Account authentication remains in post.cgi.
use utf8;
use Encode qw(decode);
use JSON::PP;
use Cwd qw(getcwd);
use lib '/var/www/html/cgi-bin';
open(my $result_out, '>&', \*STDOUT) or die "result handle";
open(STDOUT, '>', '/dev/null') or die "discard HTML";
my $json = JSON::PP->new->utf8;
my $finished = 0;
sub result {
    my ($data) = @_;
    print {$result_out} $json->encode($data) or die "write result";
    $finished = 1;
    exit 0;
}
sub leobbs_agent_error {
    result({status => 429, error => {code => 'RATE_LIMITED', message => '刷新页面过快，请稍后重试', retryAfterSeconds => 0 + $_[0]}});
}
use LBCGI;
require 'code.cgi';
require 'data/boardinfo.cgi';
require 'data/styles.cgi';
require 'data/cityinfo.cgi';
require 'bbs.lib.pl';
$usegzip = 'no';
my $succeeded = 0;
my $old_mischeader = \&mischeader;
{
    no warnings 'redefine';
    *error = sub {
        my (undef, $message) = split /&/, $_[0], 3;
        result({legacyError => decode('cp936', $message // $_[0])});
    };
    *mischeader = sub {
        my $label = decode('cp936', $_[0]);
        $succeeded = 1 if $label eq '新主题发表成功' || $label eq '回复成功';
        $old_mischeader->(@_);
    };
    *output = sub {
        die "legacy operation did not reach success" unless $succeeded;
        my $topic_id = $action eq 'addnew' ? $newthreadnumber : $intopic;
        die "invalid target" unless $topic_id =~ /\A[1-9][0-9]*\z/ && $inforum =~ /\A[1-9][0-9]*\z/;
        open(my $thread, '<:raw', "forum$inforum/$topic_id.thd.cgi") or die "read saved post";
        my @posts = <$thread>;
        close $thread;
        die "empty saved topic" unless @posts;
        my ($saved_author) = split /\t/, $posts[-1];
        die "unexpected saved author" unless lc($saved_author) eq lc($inmembername);
        result({status => 201, data => {boardId => 0 + $inforum, topicId => 0 + $topic_id, floor => scalar @posts}});
    };
}
do './post.cgi';
die "legacy worker returned without result";
