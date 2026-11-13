#!/usr/bin/perl
use strict;
use warnings;
use utf8;
use feature 'fc';
use CGI;
use Encode qw(decode encode FB_CROAK);
use HTML::Entities qw(decode_entities);
use JSON::PP;

$CGI::POST_MAX = 65536;
$CGI::DISABLE_UPLOADS = 1;
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

# Encode a UTF-8 form for the legacy CGI, which still handles authentication and writes.
sub legacy_form {
    my %allowed = map { $_ => 1 } qw(action forum topic inmembername inpassword
        CookieDate intopictitle inpost uselbcode password password2 emailaddress showemail sessionid verifynum touser msgtitle message backup adduser deluser);
    my @pairs;
    for my $key ($query->param) {
        send_json('400 Bad Request', {error => '表单字段无效'}) unless $allowed{$key};
        my $value = scalar $query->param($key);
        my $bytes = eval { encode('cp936', decode('UTF-8', $value, FB_CROAK), FB_CROAK) };
        send_json('422 Unprocessable Entity', {error => '含有旧论坛无法保存的字符，请移除 emoji 或生僻字'})
            if $@;
        $bytes =~ s/([^a-zA-Z0-9_.~-])/sprintf('%%%02X', ord($1))/ge;
        push @pairs, "$key=$bytes";
    }
    send_json('200 OK', {form => join('&', @pairs)});
}

sub forum_stats {
    my %counts;
    for my $row (rows('data/boardstats.cgi')) {
        $counts{$1} = $2 if $row =~ /^\$(lastregisteredmember|totalmembers|totalthreads|totalposts) = '([^']*)';/;
    }
    my ($postlog) = rows('data/todaypost.cgi');
    my ($day, $today, undef, $peak, $yesterday) = fields($postlog // '');
    my @date = localtime;
    my $current = sprintf '%04d/%02d/%02d', $date[5] + 1900, $date[4] + 1, $date[3];
    if ($day ne $current) {
        my @prior = localtime(time - 86400);
        my $previous = sprintf '%04d/%02d/%02d', $prior[5] + 1900, $prior[4] + 1, $prior[3];
        ($today, $yesterday) = (0, $day eq $previous ? $today : 0);
    }
    my ($counter) = rows('data/counter.cgi');
    my ($visits, $clicks, $onlinePeak, $onlinePeakAt) = fields($counter // '');
    my ($membersOnline, $guestsOnline) = (0, 0);
    for my $row (rows('data/onlinedata.cgi')) {
        my ($name, undef, $seen, undef, undef, undef, undef, undef, undef, $role) = fields($row);
        next unless defined $seen && $seen =~ /^\d+$/ && $seen >= time - 900;
        next if $role eq 'hidden';
        if ($name =~ /^\xBF\xCD\xC8\xCB/) { $guestsOnline++ }
        else { $membersOnline++ }
    }
    my ($birthday_date, undef, $birthdays) = rows('data/birthdaytoday.cgi');
    return {lastMember => text($counts{lastregisteredmember}), members => 0 + ($counts{totalmembers} || 0),
        topics => 0 + ($counts{totalthreads} || 0), replies => 0 + ($counts{totalposts} || 0),
        today => 0 + ($today || 0), yesterday => 0 + ($yesterday || 0), peak => 0 + ($peak || 0),
        online => $membersOnline + $guestsOnline, membersOnline => $membersOnline, guestsOnline => $guestsOnline,
        visits => 0 + ($visits || 0), clicks => 0 + ($clicks || 0),
        onlinePeak => 0 + ($onlinePeak || 0), onlinePeakAt => 0 + ($onlinePeakAt || 0), birthdays => ($birthday_date // '') =~ /^#\Q$current\E/ ? 0 + ($birthdays || 0) : 0};
}

sub classic_settings {
    my %values;
    for my $file (@_) {
        for my $row (rows($file)) {
            $values{$1} = $3 if $row =~ /^\s*\$(\w+)\s*=\s*(["'])(.*?)\2\s*;/;
        }
    }
    return \%values;
}

sub author_profile {
    my ($raw, $settings, $directories, $online) = @_;
    my $name = lc $raw;
    $name =~ tr/ /_/;
    return unless $name =~ /\A[^.\/\\\x00-\x1f]{2,32}\z/;
    my $bucket = ((ord(substr($name,0,1)) & 0x3c) << 3) | ((ord(substr($name,1,1)) & 0x7c) >> 2);
    for my $directory (@$directories) {
        for my $folder ($bucket, 'old') {
            my ($row) = rows("$directory/$folder/$name.cgi");
            next unless defined $row;
            my @f = fields($row);
            my $stored = lc($f[0] // '');
            $stored =~ tr/ /_/;
            next unless $stored eq $name && @f > 44;
            my $role = $f[3];
            my %roles = (ad => ['admin', '论坛坛主', 'teamad'], smo => ['smo', '论坛总版主', 'teamsmo'],
                cmo => ['cmo', '分类区版主', 'teamcmo'], mo => ['team', '论坛版主', 'teammo'],
                amo => ['amo', '论坛副版主', 'teamamo']);
            my ($color_key, $role_label, $icon) = @{$roles{$role} || [$role =~ /^rz/ ? 'rz' : 'poster', '普通会员', '']};
            my $color = $settings->{$color_key . 'namecolor'} // '';
            $color = '' unless $color =~ /\A#[0-9a-f]{6}\z/i;
            my ($posts, $replies) = split /\|/, $f[4];
            my ($bank, $deposit, undef, $loan) = split /,/, $f[40];
            my $rank = 0;
            for my $level (1..19, 'max') {
                $rank = $level if defined $settings->{"mpostmark$level"} && ($f[44] || 0) >= $settings->{"mpostmark$level"};
            }
            my $level = $settings->{"mtitle$rank"};
            my $badge = $settings->{"mgraphic$rank"};
            if ($role eq 'ad') {
                $level = $settings->{adtitle} || $level;
                $badge = $settings->{admingraphic} || $badge;
            }
            my $cash = ($posts || 0) * ($settings->{addmoney} || 0)
                + ($replies || 0) * ($settings->{replymoney} || 0)
                + ($f[27] || 0) * ($settings->{loginmoney} || 0) + ($f[30] || 0)
                - ($f[31] || 0) * ($settings->{delmoney} || 0) + ($f[39] || 0) * ($settings->{addjhhb} || 0);
            my $avatar = '/non-cgi/avatars/' . ($f[18] =~ /\A[\w-]+\z/ ? $f[18] : 'noavatar') . '.gif';
            if ($f[22] =~ m{(?:\$imagesurl|/non-cgi|https?://[^/]+/non-cgi)/((?:usravatars|avatars)/[\w.-]+\.(?:gif|png|jpe?g|webp))\z}i) {
                $avatar = "/non-cgi/$1";
            }
            $avatar = '/non-cgi/avatars/noavatar.gif' unless -f "/var/www/html$avatar";
            return {avatar => $avatar, title => $f[2] && lc($f[2]) ne 'member' ? text($f[2]) : $role_label,
                level => text($level), badge => ($badge // '') =~ /\A[\w-]+\.gif\z/ ? $badge : '',
                color => $color, roleIcon => $icon, online => $online->{lc $raw} ? 1 : 0,
                reputation => 0 + ($f[25] || 0), points => 0 + ($f[44] || 0), cash => $cash,
                currency => text($settings->{moneyname}), deposit => ($bank // '') =~ /\A-?1\z/ ? 0 + ($deposit || 0) : undef,
                loan => ($bank // '') =~ /\A-?1\z/ ? 0 + ($loan || 0) : 0,
                location => text($f[11]), flag => $f[19] =~ /\A[\w-]+\z/ ? $f[19] : 'blank',
                posts => 0 + ($posts || 0) + ($replies || 0), featured => 0 + ($f[39] || 0),
                onlineSeconds => 0 + ($f[41] || 0), joined => 0 + ($f[13] || 0), lastVisit => 0 + ($f[26] || 0)};
        }
    }
    return;
}

sub dispatch {
    if (($ENV{PATH_INFO} // '') eq '/legacy-form' && $query->request_method eq 'POST') {
        send_json('413 Payload Too Large', {error => '表单太长'}) if $query->cgi_error;
        legacy_form();
    }
    send_json('405 Method Not Allowed', {error => '仅支持 GET'}) unless $query->request_method eq 'GET';
    my $path = $ENV{PATH_INFO} // '';
    my $index = $query->param('page') // 1;
    send_json('400 Bad Request', {error => '页码无效'}) unless $index =~ /\A[1-9][0-9]{0,5}\z/;
    if ($path eq '/search') {
        my $mode = scalar $query->param('mode') // 'title';
        my $days = scalar $query->param('days') // 'any';
        my $direction = scalar $query->param('when') // 'after';
        my @boards = $query->multi_param('board');
        send_json('400 Bad Request', {error => '搜索条件无效'})
            unless $mode =~ /\A(?:title|body|both|author|reply_author|all_authors)\z/
                && $days =~ /\A(?:any|1|7|14|30|90|180|365)\z/
                && $direction =~ /\A(?:before|after)\z/
                && !grep { !/\A[1-9][0-9]{0,9}\z/ } @boards;
        my %selected = map { $_ => 1 } @boards;
        my $raw = scalar $query->param('q') // '';
        my $term = eval { decode('UTF-8', $raw, FB_CROAK) };
        send_json('400 Bad Request', {error => '请输入 1 至 80 个字符'})
            unless defined $term && $term =~ /\S/ && length($term) <= 80;
        $term =~ s/^\s+|\s+$//g;
        $term = fc($term);
        my @terms = grep { length } map { s/^\s+|\s+$//gr } split /[,，]/, $term;
        send_json('400 Bad Request', {error => '请输入关键词'}) unless @terms;
        my $matches_text = sub {
            my $value = fc($_[0]);
            return scalar grep { index($value, $_) >= 0 } @terms;
        };
        my $cutoff = $days eq 'any' ? undef : time - $days * 86400;
        my @matches;
        my @visible;
        for my $id (keys %enabled) {
            my $board = board($id) or next;
            push @visible, $board;
            next if @boards && !$selected{$id};
            for my $topic (topics($id)) {
                next if defined $cutoff && ($direction eq 'after'
                    ? $topic->{created} < $cutoff : $topic->{created} > $cutoff);
                my $found = $mode =~ /^(title|both)$/ && $matches_text->($topic->{title});
                $found ||= $mode =~ /^(author|all_authors)$/ && $matches_text->($topic->{author});
                if (!$found && $mode =~ /^(body|both|reply_author|all_authors)$/) {
                    my @posts = rows("forum$id/$topic->{id}.thd.cgi");
                    my $reply_search = $mode =~ /author/;
                    shift @posts if $reply_search;
                    for my $row (@posts) {
                        my @f = fields($row);
                        next unless @f >= 8;
                        my $body = text($f[6]);
                        next if $body =~ /LBHIDDEN|LBSALE|\[\/?(?:hide|postisdelete|adminope)/i;
                        $body =~ s/<[^>]*>|\[\/?[a-z][^\]]*\]/ /ig;
                        if ($matches_text->($reply_search ? text($f[0]) : $body)) {
                            $found = 1;
                            last;
                        }
                    }
                }
                push @matches, {%$topic, boardId => $board->{id}, boardName => $board->{name}} if $found;
            }
        }
        @matches = sort { $b->{updated} <=> $a->{updated} || $a->{boardId} <=> $b->{boardId}
            || $a->{id} <=> $b->{id} } @matches;
        send_json('200 OK', {%{page($index, @matches)}, boards => \@visible});
    }
    if ($path eq '/home') {
        my @boards = grep { defined } map { board($_) } sort { $a <=> $b } keys %enabled;
        my @latest = sort { $b->{updated} <=> $a->{updated} } map {
            my $id = $_->{id};
            map { +{%$_, boardId => $id} } topics($id)
        } @boards;
        splice @latest, 8 if @latest > 8;
        send_json('200 OK', {boards => \@boards, latest => \@latest, stats => forum_stats()});
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
            my $ubb_disabled = $raw_body =~ s/\[DISABLELBCODE\]\z//i;
            $raw_body =~ s/<br\s*\/?\s*>/\n/ig;
            my $body = text($raw_body);
            # Keep legacy visibility controls and advanced markup in the original renderer.
            my $desktop_only = $body =~ /LBHIDDEN|LBSALE|\[\/?(?:hide|postisdelete|adminope|uploadfile)/i;
            push @posts, {author => text($f[0]), created => 0 + ($f[5] || 0),
                body => $desktop_only ? '' : $body, ubb => $ubb_disabled ? JSON::PP::false : JSON::PP::true,
                desktopOnly => $desktop_only ? JSON::PP::true : JSON::PP::false,
                floor => 1 + @posts, rawAuthor => $f[0]};
        }
        send_json('404 Not Found', {error => '主题不存在'}) unless @posts;
        my $result = page($index, @posts);
        my $settings = classic_settings('data/styles.cgi', 'data/skin/leobbs.cgi',
            'data/membertitles.cgi', 'data/cityinfo.cgi');
        opendir(my $root_dir, $root) or die "Cannot read forum directory";
        my @members = sort { length($b) <=> length($a) }
            grep { /^members[[:alnum:]_]*$/ && -d "$root/$_" } readdir($root_dir);
        closedir($root_dir);
        my %online;
        for my $row (rows('data/onlinedata.cgi')) {
            my ($name, undef, $seen, undef, undef, undef, undef, undef, undef, $role, $hidden) = fields($row);
            $name =~ s/_/ /g;
            $online{lc $name} = 1 if defined $role && ($hidden // '') ne '1'
                && ($seen // '') =~ /^\d+$/ && $seen >= time - 900;
        }
        my %profiles;
        for my $post (@{$result->{items}}) {
            my $raw = delete $post->{rawAuthor};
            $profiles{$raw} = author_profile($raw, $settings, \@members, \%online)
                unless exists $profiles{$raw};
            $post->{profile} = $profiles{$raw};
        }
        send_json('200 OK', {board => $board, topic => $topic, %$result});
    }
    send_json('404 Not Found', {error => '接口不存在'});
}

eval { dispatch(); };
warn $@ if $@;
send_json('500 Internal Server Error', {error => '论坛数据暂时无法读取'});
