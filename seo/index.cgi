#!/usr/bin/perl
use strict;
use warnings;

my $root = '/var/www/html/cgi-bin';

sub lines {
    my ($path) = @_;
    open my $file, '<:raw', "$root/$path" or return;
    return <$file>;
}

sub config {
    my %values;
    for my $path (@_) {
        for my $line (lines($path)) {
            if ($line =~ /^\s*\$(\w+)\s*=\s*(['"])(.*?)\2\s*;/) {
                $values{$1} = $3;
            } elsif ($line =~ /^\s*\$(\w+)\s*=\s*(\d+)\s*;/) {
                $values{$1} = $2;
            }
        }
    }
    return %values;
}

sub xml {
    my ($value) = @_;
    $value =~ s/&/&amp;/g;
    $value =~ s/</&lt;/g;
    $value =~ s/>/&gt;/g;
    return $value;
}

sub response {
    my ($type, $body) = @_;
    print "Content-Type: $type; charset=utf-8\r\nCache-Control: no-store\r\n\r\n$body";
}

my $path = ($ENV{REQUEST_URI} // '/') =~ s/\?.*//r;
if ($path eq '/') {
    my $mobile = ($ENV{HTTP_USER_AGENT} // '') =~ /Android|iPhone|iPad|iPod|Mobile/i;
    my $target = $mobile ? '/m/' : '/cgi-bin/leobbs.htm';
    print "Status: 302 Found\r\nLocation: $target\r\nVary: User-Agent\r\nCache-Control: no-store\r\nContent-Type: text/plain\r\n\r\n";
    exit;
}

my %site = config('data/boardinfo.cgi', 'data/styles.cgi');
my $base = $ENV{LEOBBS_PUBLIC_ORIGIN} || ($site{boardurl} // '') =~ s{/cgi-bin/?$}{}r;
$base =~ s{/$}{};
if ($base !~ m{\Ahttps?://(?:[A-Za-z0-9.-]+|\[[0-9A-Fa-f:]+\])(?::[0-9]{1,5})?\z}) {
    print "Status: 503 Service Unavailable\r\n";
    response('text/plain', "Set LEOBBS_PUBLIC_ORIGIN to the public site origin.\n");
    exit;
}

if ($path eq '/robots.txt') {
    my @blocked = qw(admin install loginout register checkname messanger massmsg
        search postings post poll delpost editpost profile resetusr wap_login wap_reg
        wap_sms wap_sms_all wap_smssave wap_smssend);
    my $rules = "User-agent: *\n";
    $rules .= "Disallow: /cgi-bin/$_.cgi\n" for @blocked;
    $rules .= "Disallow: /cgi-bin/$_/\n" for qw(data boarddata cache members messages search);
    $rules .= "Disallow: /api/\nDisallow: /m/search\nSitemap: $base/sitemap.xml\n";
    response('text/plain', $rules);
    exit;
}

# Mirror the classic guest gates in forums.cgi/topic.cgi. Scheduled closures
# and customized boards are excluded unless their public settings are explicit.
sub guest_can_read {
    my ($settings, $forum) = @_;
    return 0 if ($settings->{guestregistered} // '') ne 'on';
    return 0 if ($settings->{mainoff} || 0) || ($settings->{mainonoff} || 0);
    return 0 if grep { length($settings->{$_} // '') } qw(yxz allowusers);
    return 0 if grep { ($settings->{$_} || 0) > 0 } qw(enterminweiwang enterminmony enterminjf);
    return 1 unless $forum;
    return $forum->[8] eq 'no' && !$forum->[17] && $forum->[18] eq 'no'
        && $forum->[19] eq 'yes' && $forum->[9] ne 'cert';
}

my @urls;
if (guest_can_read(\%site)) {
    push @urls, '/cgi-bin/leobbs.htm';
    my %seen;
    for my $row (lines('data/allforums.cgi')) {
        my ($id) = split /\t/, $row;
        next unless $id =~ /\A[1-9][0-9]{0,9}\z/ && !$seen{$id}++;
        my ($record) = lines("forum$id/foruminfo.cgi");
        next unless defined $record;
        $record =~ s/\r?\n\z//;
        my @forum = split /\t/, $record, -1;
        next unless @forum >= 20 && $forum[0] eq $id;
        # Board overrides can contain arbitrary legacy Perl. Do not infer
        # public visibility from an override that we cannot evaluate safely.
        next if -e "$root/data/style$id.cgi" || $forum[1] =~ /^childforum-/;
        next unless guest_can_read(\%site, \@forum);
        push @urls, "/cgi-bin/forums-$id-0.htm";
        my %topics;
        for my $index (lines("boarddata/listno$id.cgi")) {
            $index =~ s/\r?\n\z//;
            next unless $index =~ /\A[1-9][0-9]{0,9}\z/ && !$topics{$index}++;
            my @posts = lines("forum$id/$index.thd.cgi");
            next unless @posts;
            next if grep { /LBHIDDEN|LBSALE|\[\/?(?:hide|postisdelete|adminope)/i } map { (split /\t/, $_, 9)[6] // '' } @posts;
            push @urls, "/cgi-bin/topic-$id-$index-0-0-.htm";
        }
    }
}
my $body = qq{<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n};
$body .= '  <url><loc>' . xml($base . $_) . "</loc></url>\n" for @urls;
response('application/xml', $body . "</urlset>\n");
