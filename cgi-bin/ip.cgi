#!/usr/bin/perl
#####################################################
#  LEO SuperCool BBS / LeoBBS X / 雷傲极酷超级论坛  #
#####################################################
# 基于山鹰(糊)、花无缺制作的 LB5000 XP 2.30 免费版  #
#   新版程序制作 & 版权所有: 雷傲科技 (C)(R)2004    #
#####################################################
#      主页地址： http://www.LeoBBS.com/            #
#      论坛地址： http://bbs.LeoBBS.com/            #
#####################################################

BEGIN {
    $startingtime=(times)[0]+(times)[1];
    foreach ($0,$ENV{'PATH_TRANSLATED'},$ENV{'SCRIPT_FILENAME'}){
    	my $LBPATH = $_;
    	next if ($LBPATH eq '');
    	$LBPATH =~ s/\\/\//g; $LBPATH =~ s/\/[^\/]+$//o;
        unshift(@INC,$LBPATH);
    }
}

use LBCGI;
require "data/boardinfo.cgi";
use testinfo qw(ipwhere osinfo browseinfo);

print "Content-type: text/html\n\n";

sub lb_is_public_ip {
    my $ip = shift || '';
    return 0 unless $ip =~ /^\d{1,3}(?:\.\d{1,3}){3}$/;
    my @p = split(/\./, $ip);
    foreach my $n (@p) { return 0 if $n > 255; }
    return 0 if $p[0] == 0 || $p[0] == 10 || $p[0] == 127 || $p[0] >= 224;
    return 0 if $p[0] == 100 && $p[1] >= 64 && $p[1] <= 127;
    return 0 if $p[0] == 169 && $p[1] == 254;
    return 0 if $p[0] == 172 && $p[1] >= 16 && $p[1] <= 31;
    return 0 if $p[0] == 192 && $p[1] == 168;
    return 1;
}

sub lb_forwarded_ip {
    foreach my $header ($ENV{'HTTP_X_REAL_IP'}, $ENV{'HTTP_X_FORWARDED_FOR'}) {
        next if !defined($header) || $header eq '' || $header =~ /unknown/i;
        foreach my $candidate (split(/\s*,\s*/, $header)) {
            $candidate =~ s/^\s+|\s+$//g;
            return $candidate if &lb_is_public_ip($candidate);
        }
    }
    return '';
}

$ipaddress     = $ENV{"REMOTE_ADDR"};
$trueipaddress = &lb_forwarded_ip();
$trueipaddress = $ipaddress if ($trueipaddress eq "");
$fromwhere1 = &ipwhere("$trueipaddress");
print "您的 IP 地址：$trueipaddress，来源鉴定：$fromwhere1<BR>";
if ($ipaddress ne $trueipaddress) { $fromwhere2 = &ipwhere("$ipaddress"); print "代理 IP 地址：$ipaddress，来源鉴定：$fromwhere2<BR>"; } else { print "代理 IP 地址未知(没有使用代理、代理服务器 IP 显示被禁止)"; }
eval { $osinfo=&osinfo(); };
if ($@) { $osinfo="Unknow"; }
eval { $browseinfo=&browseinfo(); };
if ($@) { $browseinfo="Unknow"; }
print "<BR><BR>您的操作系统是：$osinfo，使用的浏览器是：$browseinfo<BR>($ENV{\"HTTP_USER_AGENT\"})<BR>";
