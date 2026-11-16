#!/usr/bin/perl
# Resolve legacy account, category moderators and per-board settings in a fresh
# process per board. This is a delegation eligibility check, not a posting bypass;
# post.cgi continues to enforce live flood, topic, content and account restrictions.
use utf8;
use lib '/var/www/html/cgi-bin';
use LBCGI;
use Encode qw(decode);
use JSON::PP;
require 'code.cgi';
require 'data/boardinfo.cgi';
require 'data/styles.cgi';
require 'data/cityinfo.cgi';
require 'bbs.lib.pl';
my $json = JSON::PP->new->utf8;
sub respond { print $json->encode($_[0]); exit 0; }
$inforum = $ENV{AGENT_BOARD_ID};
respond(undef) unless $inforum =~ /\A[1-9][0-9]{0,9}\z/;
$query = new LBCGI;
$inmembername = $query->cookie('amembernamecookie');
&getmember($inmembername, 'no');
respond(undef) if $userregistered eq 'no' || $membercode =~ /^(?:banned|masked)$/ || $password ne $query->cookie('apasswordcookie');
require "data/style$inforum.cgi" if -e "data/style$inforum.cgi";
&moderator($inforum);
respond(undef) unless $forumid eq $inforum;
respond(undef) if $postopen eq 'no' || $startnewthreads eq 'onlysub';
my $privileged = $membercode =~ /^(?:ad|smo)$/ || $inmembmod eq 'yes';
respond(undef) if $yxz ne '' && index($yxz, ",$membercode,") < 0;
respond(undef) if $allowusers ne '' && $membercode ne 'ad' && index(lc(",$allowusers,"), lc(",$inmembername,")) < 0;
# No transient forum-password cookies are delegated to Agent Tokens.
respond(undef) if $privateforum eq 'yes' && !$privileged && $allowedentry{$inforum} ne 'yes';
if (!$privileged) {
    respond(undef) if $enterminweiwang > 0 && $rating < $enterminweiwang;
    my $cash = $numberofposts * $addmoney + $numberofreplys * $replymoney + $visitno * $loginmoney + $mymoney - $postdel * $delmoney + $jhcount * $addjhhb;
    respond(undef) if $enterminmony > 0 && $cash < $enterminmony;
    respond(undef) if $enterminjf > 0 && $jifen < $enterminjf;
}
my $staff = $membercode =~ /^(?:ad|smo|cmo|mo|amo)$/ || $inmembmod eq 'yes';
my $certified = $staff || $membercode =~ /^rz/;
respond(undef) if !$certified && $onlinepost > 0 && $onlinetime < $onlinepost;
respond(undef) if !$staff && $deletepercent > 0 && $numberofposts + $numberofreplys > 0 && $postdel / ($numberofposts + $numberofreplys) >= $deletepercent / 100;
respond(undef) if $startnewthreads eq 'no' && !$privileged;
respond(undef) if $startnewthreads eq 'cert' && !$certified;
my @scopes;
push @scopes, 'topics:write' if ($privileged || $postminjf <= 0 || $jifen >= $postminjf)
    && ($startnewthreads ne 'follow' || $staff) && ($mastpostatt ne 'yes' || $privileged);
push @scopes, 'replies:write' if $privileged || $replyminjf <= 0 || $jifen >= $replyminjf;
respond({id => 0 + $inforum, name => decode('cp936', $forumname), scopes => \@scopes});
