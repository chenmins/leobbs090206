#####################################################
#  LEO SuperCool BBS / LeoBBS X / 雷傲极酷超级论坛  #
#####################################################
# 基于山鹰(糊)、花无缺制作的 LB5000 XP 2.30 免费版  #
#   新版程序制作 & 版权所有: 雷傲科技 (C)(R)2004    #
#####################################################
#      主页地址： http://www.LeoBBS.com/            #
#      论坛地址： http://bbs.LeoBBS.com/            #
#####################################################

package WebGzip;
use strict;

my $level = 9;
my $status = undef;my $callback = undef;

sub import {setLevel($_[1]);if (!defined getAbility()) {startCapture();}}
END {flush();}

sub flush {
my $data = stopCapture(); return if !defined $data;
my ($headers, $body) = split /\r?\n\r?\n/, $data, 2;
my ($newBody, $newHeaders, $stat) = ob_gzhandler($body, $headers);
$status = $stat;
if ($callback) {$callback->($newBody, $newHeaders, $body) or return;}
binmode(STDOUT);
#print "Content-type: text/html\n\n";
print $newHeaders;
print "\r\n\r\n$status"; 
print $newBody;
}
sub getAbility {
if (!$ENV{SCRIPT_NAME}) {return "no: not a CGI script";}
my $acc = $ENV{HTTP_ACCEPT_ENCODING}||"";
if ($acc !~ /\bgzip\b/i) {return "no: incompatible browser";}
if (!eval { require Compress::Zlib }) {	return "no: Compress::Zlib not found";}
return undef;
}
sub isCompressibleType {my ($type) = @_;return $type =~ m{^text/}i;}
sub setCallback {my $prev = $callback;$callback = $_[0];return $prev;}
sub setLevel {my $prev = $level;$level = defined $_[0]? $_[0]:9;return $prev;}
sub getStatus {return $status;}
sub ob_gzhandler {
my ($body, $h) = @_;
$h ||= "";my $status = undef;my $ContentEncoding = undef;my $ContentType = undef;my $Status = undef;my @headers = ();
foreach (split /\r?\n/, $h) {
if (/^Content[-_]Encoding:\s*(.*)/i) {$ContentEncoding = $1;next;} 
if (/^Content[-_]Type:\s*(.*)/i) {$ContentType = $1;}
if (/^Status:\s*(\d+)/i) {$Status = $1;}
push @headers, $_ if $_;
}
my $needCompress = 1;
if (defined $ContentType && !isCompressibleType($ContentType)) {$ContentType ||= "undef";$status = "no: incompatible Content-type ($ContentType)";$needCompress = undef;}
if ($Status && $Status ne 200) {$status = "no: Status must be 200 (given $Status)";$needCompress = undef;}
if (defined($status=getAbility())) {$needCompress = undef;}
if ($needCompress) {
$ContentEncoding = "gzip" . ($ContentEncoding? ", $ContentEncoding" : "")
if !$ContentEncoding || $ContentEncoding !~ /\bgzip\b/i;
push @headers, "Content-Encoding: $ContentEncoding";push @headers, "Vary: Accept-Encoding";
}
my $headers = join "\r\n", @headers;my $out = $needCompress? deflate_gzip($body, $level) : $body;
return wantarray? ($out, $headers, $status) : $out;
}
sub deflate_gzip {
my ($d, $st) = Compress::Zlib::deflateInit(-Level => defined $_[1]? $_[1] : 9);my ($out, $Status) = $d->deflate($_[0]);my ($outF, $StatusF) = $d->flush();$out = $out.$outF;
my $pre = pack('cccccccc', 0x1f,0x8b,0x08,0x00,0x00,0x00,0x00,0x00);
$out = $pre . substr($out, 0, -4) . pack('V', Compress::Zlib::crc32($_[0])) . pack('V', length($_[0]));
return $out;
}
my $capture = undef;
sub startCapture {return if $capture;$capture = tie *STDOUT, "WebGzip::Tie";}
sub stopCapture {
return undef if !$capture;
my $obj = tied *STDOUT;my $data = join "", @$obj;
untie(*STDOUT);
return $data;
}
package WebGzip::Tie;
sub TIEHANDLE  { return bless [], $_[0] } 
sub WRITE      { my $th = shift; push @$th, @_; }
sub PRINT      { my $th = shift; push @$th, @_; }
sub PRINTF     { my $th = shift; push @$th, sprintf @_; }
sub CLOSE      { WebGzip::flush() }
sub BINMODE    { }
return 1;
