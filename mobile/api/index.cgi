#!/usr/bin/perl
use strict;
use warnings;
use utf8;
use CGI;
use Encode qw(decode FB_CROAK);
use HTML::Entities qw(decode_entities);
use JSON::PP;

my $query = CGI->new;
my $root = '/var/www/html/cgi-bin';
my %enabled = map { $_ => 1 } grep { /\A[1-9][0-9]*\z/ }
    split /,/, $ENV{LEOBBS_MOBILE_PUBLIC_BOARDS} // '';
my $json = JSON::PP->new->utf8;

sub send_json {
    my ($status, $data) = @_;
    print "Status: $status\r\nContent-Type: application/json; charset=utf-8\r\n";
    print "Cache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\n\r\n";
    print $json->encode($data);
    exit;
}

sub rows {
    my ($path) = @_;
    open my $file, '<:raw', "$root/$path" or return;
    return <$file>;
}

# Preserve empty trailing columns in the legacy tab-separated records.
sub fields {
    my ($row) = @_;
    $row =~ s/\r?\n\z//;
    return split /\t/, $row, -1;
}

# Decode at the API boundary so legacy offsets and separators stay byte-based.
sub text {
    my ($raw) = @_;
    $raw //= '';
    return decode_entities(decode('cp936', $raw, FB_CROAK));
}

sub board {
    my ($id) = @_;
    return unless $enabled{$id};
    # Apply the anonymous-read checks before opening any topic records.
    my @styles = rows('data/styles.cgi');
    return unless grep { /^\s*\$guestregistered\s*=\s*["']on["']\s*;/ } @styles;
    my ($row) = rows("forum$id/foruminfo.cgi");
    return unless defined $row;
    my @f = fields($row);
    return unless @f >= 20 && $f[0] eq $id && $f[1] !~ /^childforum-/;
    return unless $f[8] eq 'no' && $f[18] eq 'no' && $f[19] eq 'yes' && $f[17] eq '';
    return unless $f[9] eq 'yes' || $f[9] eq 'all';
    return if -e "$root/data/style$id.cgi";
    # LeoBBS updates the live counters separately from the forum settings.
    my ($stats) = rows("boarddata/foruminfo$id.cgi");
    my (undef, $topics, $posts) = fields($stats // '');
    return {id => 0 + $id, category => text($f[1]), name => text($f[3]),
        description => text($f[4]), topics => 0 + ($topics || 0), posts => 0 + ($posts || 0)};
}

sub topics {
    my ($id) = @_;
    my @topics;
    # The board index holds ordered IDs. Each topic has a separate metadata record.
    for my $row (rows("boarddata/listno$id.cgi")) {
        chomp $row;
        $row =~ s/\r\z//;
        next unless $row =~ /\A[1-9][0-9]{0,9}\z/;
        my ($metadata) = rows("forum$id/$row.pl");
        next unless defined $metadata;
        my ($topic, $title, undef, $state, $replies, $views, $author,
            $created, undef, $updated, $icon) = fields($metadata);
        next unless $topic eq $row && defined $updated;
        my $label = text($title);
        # The classic renderer strips this internal title prefix too.
        $label =~ s/^＊＃！＆＊//;
        push @topics, {id => 0 + $topic, title => $label, state => text($state),
            author => text($author), updated => 0 + ($updated || 0), created => 0 + ($created || 0),
            replies => 0 + ($replies || 0), views => 0 + ($views || 0),
            icon => defined $icon && $icon =~ /\A([0-9]{2})(?:\.gif)?\z/ ? $1 : '00'};
    }
    return @topics;
}

sub page {
    my ($index, @items) = @_;
    my $pages = int((@items + 19) / 20) || 1;
    my $start = ($index - 1) * 20;
    my $end = $start + 19 < $#items ? $start + 19 : $#items;
    return {page => 0 + $index, pages => $pages, items => [@items[$start .. $end]]};
}

sub dispatch {
    send_json('405 Method Not Allowed', {error => '仅支持 GET'}) unless $query->request_method eq 'GET';
    my $path = $ENV{PATH_INFO} // '';
    my $index = $query->param('page') // 1;
    send_json('400 Bad Request', {error => '页码无效'}) unless $index =~ /\A[1-9][0-9]{0,5}\z/;
    if ($path eq '/home') {
        my @boards = grep { defined } map { board($_) } sort { $a <=> $b } keys %enabled;
        my @latest = sort { $b->{updated} <=> $a->{updated} } map {
            my $id = $_->{id};
            map { +{%$_, boardId => $id} } topics($id)
        } @boards;
        splice @latest, 8 if @latest > 8;
        send_json('200 OK', {boards => \@boards, latest => \@latest});
    }
    if ($path =~ m{\A/boards/([1-9][0-9]{0,9})(?:/topics/([1-9][0-9]{0,9}))?\z}) {
        my ($id, $topic_id) = ($1, $2);
        my $board = board($id);
        send_json('404 Not Found', {error => '版块不存在'}) unless $board;
        my @topics = topics($id);
        send_json('200 OK', {board => $board, %{page($index, @topics)}}) unless defined $topic_id;
        my ($topic) = grep { $_->{id} == $topic_id } @topics;
        send_json('404 Not Found', {error => '主题不存在'}) unless $topic;
        my @posts;
        for my $row (rows("forum$id/$topic_id.thd.cgi")) {
            my @f = fields($row);
            next unless @f >= 8;
            my $raw_body = $f[6];
            $raw_body =~ s/\[DISABLELBCODE\]\z//i;
            $raw_body =~ s/<br\s*\/?\s*>/\n/ig;
            my $body = text($raw_body);
            # Keep legacy visibility controls and advanced markup in the original renderer.
            my $desktop_only = $body =~ /\[|<|>/;
            push @posts, {author => text($f[0]), created => 0 + ($f[5] || 0),
                body => $desktop_only ? '' : $body, desktopOnly => $desktop_only ? JSON::PP::true : JSON::PP::false,
                floor => 1 + @posts};
        }
        send_json('404 Not Found', {error => '主题不存在'}) unless @posts;
        send_json('200 OK', {board => $board, topic => $topic, %{page($index, @posts)}});
    }
    send_json('404 Not Found', {error => '接口不存在'});
}

eval { dispatch(); };
warn $@ if $@;
send_json('500 Internal Server Error', {error => '论坛数据暂时无法读取'});
