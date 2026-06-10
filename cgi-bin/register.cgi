#!/usr/bin/perl
#####################################################
#  LEO SuperCool BBS / LeoBBS X / À×°Á¼«¿á³¬¼¶ÂÛÌ³  #
#####################################################
# »ùÓÚÉ½Ó¥(ºı)¡¢»¨ÎŞÈ±ÖÆ×÷µÄ LB5000 XP 2.30 Ãâ·Ñ°æ  #
#   ĞÂ°æ³ÌĞòÖÆ×÷ & °æÈ¨ËùÓĞ: À×°Á¿Æ¼¼ (C)(R)2004    #
#####################################################
#      Ö÷Ò³µØÖ·£º http://www.LeoBBS.com/            #
#      ÂÛÌ³µØÖ·£º http://bbs.LeoBBS.com/            #
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
$LBCGI::POST_MAX=1000000;
$LBCGI::DISABLE_UPLOADS = 0;
$LBCGI::HEADERS_ONCE = 1;
use MAILPROG qw(sendmail);
require "data/boardinfo.cgi";
require "data/cityinfo.cgi";
require "data/styles.cgi";
require "bbs.lib.pl";
$|++;

$thisprog = "register.cgi";
eval ('$complevel = 9 if ($complevel eq ""); use WebGzip($complevel); $gzipused = 1;') if ($usegzip eq "yes");

$query = new LBCGI;

if ($COOKIE_USED eq 2 && $mycookiepath ne "") { $cookiepath = $mycookiepath; } elsif ($COOKIE_USED eq 1) { $cookiepath =""; }
else {
    $boardurltemp =$boardurl;
    $boardurltemp =~ s/http\:\/\/(\S+?)\/(.*)/\/$2/;
    $cookiepath = $boardurltemp;
    $cookiepath =~ s/\/$//;
#    $cookiepath =~ tr/A-Z/a-z/;
}

$addme=$query->param('addme');

$inforum  = $query -> param('forum');
&error("´ò¿ªÎÄ¼ş&ÀÏ´ó£¬±ğÂÒºÚÎÒµÄ³ÌĞòÑ½£¡") if (($inforum) && ($inforum !~ /^[0-9]+$/));

&ipbanned; #·âÉ±Ò»Ğ© ip

if ($arrowavaupload ne "on") { undef $addme; }
$inselectstyle   = $query->cookie("selectstyle");
$inselectstyle   = $skinselected if ($inselectstyle eq "");
if (($inselectstyle ne "")&&(-e "${lbdir}data/skin/${inselectstyle}.cgi")) { require "${lbdir}data/skin/${inselectstyle}.cgi"; }
if ($catbackpic ne "")  { $catbackpic = "background=$imagesurl/images/$skin/$catbackpic"; }

if ($regonoff == 2) {
   $regonoff = 1;
   $regonoffinfo = "1";
   my (undef, undef, $hour, $mday, undef, undef, $wday, undef) = localtime(time + $timezone * 3600);
   $regautovalue =~ s/[^\d\-]//sg;
   my ($starttime, $endtime) = split(/-/, $regautovalue);
   if ($regauto eq "day") {
	$regonoff = 0 if ($hour == $starttime && $endtime eq "");
	$regonoff = 0 if ($hour >= $starttime && $hour < $endtime);
   }
   elsif ($regauto eq "week") {
	$wday = 7 if ($wday == 0);
	$regonoff = 0 if ($wday == $starttime && $endtime eq "");
	$regonoff = 0 if ($wday >= $starttime && $wday <= $endtime);
   }
   elsif ($regauto eq "month") {
	$regonoff = 0 if ($mday == $starttime && $endtime eq "");
	$regonoff = 0 if ($mday >= $starttime && $mday <= $endtime);
   }
}
if ($regonoff == 1) {
    $inmembername = $query->cookie("amembernamecookie"); 
    $inpassword   = $query->cookie("apasswordcookie"); 
    $inmembername =~ s/[\a\f\n\e\0\r\t\`\~\!\@\#\$\%\^\&\*\(\)\+\=\\\{\}\;\|\'\:\"\,\.\/\<\>\?]//isg;
    $inpassword =~ s/[\a\f\n\e\0\r\t\|\@\;\#\{\}\$]//isg;
    unless ($inmembername eq "" || $inmembername eq "¿ÍÈË") { &getmember("$inmembername"); &error("ÆÕÍ¨´íÎó&´ËÓÃ»§¸ù±¾²»´æÔÚ£¡") if ($userregistered eq "no");	&error("ÆÕÍ¨´íÎó&ÂÛÌ³ÃÜÂëÓëÓÃ»§Ãû²»Ïà·û£¬ÇëÖØĞÂµÇÂ¼£¡") if ($inpassword ne $password);  $regonoff = 0 if ($membercode eq "ad"); } 
}

for ('inmembername','password','password2','emailaddress','showemail','homepage','oicqnumber','icqnumber','newlocation','recommender',
     'interests','signature','timedifference','useravatar','action','personalavatar','personalwidth','personalheight','mobilephone',
     'sex','education','marry','work','year','month','day','userflag','userxz','usersx') {
    next unless defined $_;
    next if $_ eq 'SEND_MAIL';
    $tp = $query->param($_);
    $tp = &unHTML("$tp");
    ${$_} = $tp;
}
$recommender =~ s/[\a\f\n\e\0\r\t\`\~\!\@\#\$\%\^\&\*\(\)\+\=\\\{\}\;\|\'\:\"\,\.\/\<\>\?]//isg;

&error("ÂÛÌ³ÃÜÂëÌáÊ¾ÎÊÌâºÍ´ğ°¸&ÂÛÌ³ÃÜÂëÌáÊ¾ÎÊÌâºÍ´ğ°¸ÖĞ£¬²»ÔÊĞíÓĞ·Ç·¨×Ö·û£¬Çë¸ü»»ÌáÎÊºÍ´ğ°¸£¡") if ($query -> param('getpassq') =~ /[\||\a|\f|\n|\e|\0|\r|\t]/ || $query -> param('getpassa') =~ /[\||\a|\f|\n|\e|\0|\r|\t]/);
$userquestion = $query -> param('getpassq')."|".$query -> param('getpassa'); 
$userquestion = "" if ($passwordverification eq "yes" && $emailfunctions ne "off");

$helpurl = &helpfiles("ÓÃ»§×¢²á");
$helpurl = qq~$helpurl<img src=$imagesurl/images/$skin/help_b.gif border=0></span>~;

if ($arrawsignpic eq "on")      { $signpicstates = "ÔÊĞí";     } else { $signpicstates = "½ûÖ¹";     }
if ($arrawsignflash eq "on")    { $signflashstates = "ÔÊĞí";   } else { $signflashstates = "½ûÖ¹";   }
if ($arrawsignfontsize eq "on") { $signfontsizestates = "ÔÊĞí";} else { $signfontsizestates = "½ûÖ¹";}
if ($arrawsignsound eq "on")    { $signsoundstates = "ÔÊĞí";   } else { $signsoundstates = "½ûÖ¹";   }

&mischeader("ÓÃ»§×¢²á");
$output .= qq~<p><SCRIPT>valigntop()</SCRIPT><table cellpadding=0 cellspacing=0 width=$tablewidth bgcolor=$tablebordercolor align=center>
<tr><td><table cellpadding=6 cellspacing=1 width=100%>
~;

if ($regonoff eq 1) {
    if ($regonoffinfo eq "1") {
        if ($regauto eq "day") { $regauto = "Ã¿Ìì"; } elsif ($regauto eq "week") { $regauto = "Ã¿ÖÜ"; } elsif ($regauto eq "month") { $regauto = "Ã¿ÔÂ"; }
        $regauto = "£¬¿ª·Å×¢²áÊ±¼ä£º$regauto $regautovalue £¡";
    }
    else { $regauto = ""; }

    $output .= qq~<tr><td bgcolor=$titlecolor $catbackpic align=center><font color=$fontcolormisc><b>¶Ô²»Æğ£¬ÂÛÌ³Ä¿Ç°ÔİÊ±²»ÔÊĞí×¢²áĞÂÓÃ»§$regauto</b>
    </td></tr><td bgcolor=$miscbackone align=center><font color=$fontcolormisc size=3><BR><BR>~;
    if ($noregwhynot ne "") { $noregwhynot=&HTML($noregwhynot); $noregwhynot =~ s/\n/<BR>/isg;$output.=qq~$noregwhynot~; }
                       else { $output.=qq~ÓÉÓÚÒ»Ğ©ÌØÊâµÄÔ­Òò£¬±¾ÂÛÌ³ÔİÊ±²»½ÓÊÜÓÃ»§×¢²á£¡~; }
    $output.=qq~<BR><BR><BR></td></tr></table></td></tr></table><SCRIPT>valignend()</SCRIPT>~;
}
elsif ($action eq "addmember") {
    &error("³ö´í&Çë²»ÒªÓÃÍâ²¿Á¬½Ó±¾³ÌĞò£¡") if (($ENV{'HTTP_REFERER'} !~ /$ENV{'HTTP_HOST'}/i && $ENV{'HTTP_REFERER'} ne '' && $ENV{'HTTP_HOST'} ne '')&&($canotherlink ne "yes"));
    $membercode    = "me";
    $membertitle   = "Member";
    $numberofposts = "0|0";
    $joineddate    = time;
    $lastgone      = $joineddate;
    $mymoney	   = $joinmoney;
    $jifen	   = $joinjf;
    $jhmp          = "ÎŞÃÅÎŞÅÉ";
    $lastpostdate  = "Ã»ÓĞ·¢±í¹ı";
    $emailaddress  = lc($emailaddress);
    
    if (($inmembername eq "")||($emailaddress eq "")) {
        &error("ÓÃ»§×¢²á&ÇëÊäÈëÓÃ»§ÃûºÍÓÊ¼şµØÖ·£¬ÕâĞ©ÊÇ±ØĞèµÄ£¡");
    }

    $ipaddress     = $ENV{'REMOTE_ADDR'};
    my $trueipaddress = $ENV{'HTTP_X_FORWARDED_FOR'};
    $trueipaddress = $ipaddress if ($trueipaddress eq "" || $trueipaddress =~ m/a-z/i || $trueipaddress =~ m/^192\.168\./ || $trueipaddress =~ m/^10\./);
    my $trueipaddress1 = $ENV{'HTTP_CLIENT_IP'};
    $trueipaddress = $trueipaddress1 if ($trueipaddress1 ne "" && $trueipaddress1 !~ m/a-z/i && $trueipaddress1 !~ m/^192\.168\./ && $trueipaddress1 !~ m/^10\./);
    $ipaddress = $trueipaddress;
    $year =~ s/\D//g;
    $year = "19$year"if ($year < 1900 && $year ne "");
    my (undef, undef, undef, undef, undef, $yeartemp, undef, undef) = localtime(time + $timezone * 3600);
    $yeartemp = 1900 + $yeartemp if ($yeartemp < 1900);
    if ($year ne "") {
        &error("ÓÃ»§×¢²á&ÇëÕıÈ·ÊäÈëÄãµÄ³öÉúÄê·İ£¡") if ($year <= 1900 || $year >= $yeartemp - 3);
    }
    if (($year eq "")||($month eq "")||($day eq "")) { $year  = "";$month = "";$day   = "";}
    $born = "$year/$month/$day";

    if ($born ne "//") { #¿ªÊ¼×Ô¶¯ÅĞ¶ÏĞÇ×ù
    	if ($month eq "01") {
    	    if (($day >= 1)&&($day <=19)) { $userxz = "z10"; }
    	    else { $userxz = "z11"; }
    	}
        elsif ($month eq "02") {
    	    if (($day >= 1)&&($day <=18)) { $userxz = "z11"; }
    	    else { $userxz = "z12"; }
        }
        elsif ($month eq "03") {
    	    if (($day >= 1)&&($day <=20)) { $userxz = "z12"; }
    	    else { $userxz = "z1"; }

        }
        elsif ($month eq "04") {
    	    if (($day >= 1)&&($day <=19)) { $userxz = "z1"; }
    	    else { $userxz = "z2"; }
        }
        elsif ($month eq "05") {
    	    if (($day >= 1)&&($day <=20)) { $userxz = "z2"; }
    	    else { $userxz = "z3"; }
        }
        elsif ($month eq "06") {
    	    if (($day >= 1)&&($day <=21)) { $userxz = "z3"; }
    	    else { $userxz = "z4"; }
        }
        elsif ($month eq "07") {
    	    if (($day >= 1)&&($day <=22)) { $userxz = "z4"; }
    	    else { $userxz = "z5"; }
        }
        elsif ($month eq "08") {
    	    if (($day >= 1)&&($day <=22)) { $userxz = "z5"; }
    	    else { $userxz = "z6"; }
        }
        elsif ($month eq "09") {
    	    if (($day >= 1)&&($day <=22)) { $userxz = "z6"; }
    	    else { $userxz = "z7"; }
        }
        elsif ($month eq "10") {
    	    if (($day >= 1)&&($day <=23)) { $userxz = "z7"; }
    	    else { $userxz = "z8"; }
        }
        elsif ($month eq "11") {
    	    if (($day >= 1)&&($day <=21)) { $userxz = "z8"; }
    	    else { $userxz = "z9"; }
        }
        elsif ($month eq "12") {
    	    if (($day >= 1)&&($day <=21)) { $userxz = "z9"; }
    	    else { $userxz = "z10"; }
        }
    }

	my $charone = substr($emailaddress, 0, 1);
	$charone = lc($charone);
	$charone = ord($charone);
	if ($oneaccountperemail eq "yes") {
	    mkdir ("${lbdir}data/lbemail", 0777) if (!(-e "${lbdir}data/lbemail"));
	    chmod(0777,"${lbdir}data/lbemail");

	    $/ = "";
	    open (MEMFILE, "${lbdir}data/lbemail/$charone.cgi");
 	    my $allmemberemails = <MEMFILE>;
 	    close(MEMFILE);
	    $/ = "\n";
	    $allmemberemails = "\n$allmemberemails\n";
	    chomp($allmemberemails);
	    $allmemberemails = "\t$allmemberemails";

	    if ($allmemberemails =~ /\n$emailaddress\t(.+?)\n/i) {
		&error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬ÕâÊäÈëµÄ Email ÒÑ¾­±»×¢²áÓÃ»§£º<u>$1</u> Ê¹ÓÃÁË");
	    }
	}

	#ÓÊ¼şÏŞÖÆ _S
	my $allow_eamil_file = "$lbdir" . "data/allow_email.cgi";
	if(-e $allow_eamil_file){
		open(AEFILE,$allow_eamil_file);
		my $allowtype = <AEFILE>;
		my $allowmail = <AEFILE>;
		close(AEFILE);
		chomp $allowtype;
		chomp $allowmail;
		my $check_result = 0;
		my $get_email_server = substr($emailaddress,rindex($emailaddress,'@')+1);
		if ($allowmail ne "") {
			my @allowmail = split(/\t/,$allowmail);
			chomp @allowmail;
			foreach (@allowmail){
				next if($_ eq "");
				if(lc($get_email_server) eq lc($_)){
					$check_result = 1;
					last;
				}
			}
		    if ($allowtype eq "allow") {
			if($check_result == 0){
				&error("ÓÃ»§×¢²á&±ØĞèÊ¹ÓÃÖ¸¶¨µÄÓÊÏä²ÅÄÜ×¢²á£¡<a href=\"javascript:openScript('dispemail.cgi',200,300);\">[ÁĞ±í]</a>");
			}
		    } else {
			if ($check_result == 1) {
				&error("ÓÃ»§×¢²á&ÄúÌá¹©µÄÓÊÏä±»½ûÖ¹Ê¹ÓÃ×¢²á£¡<a href=\"javascript:openScript('dispemail.cgi',200,300);\">[ÁĞ±í]</a>");
			}
		    }
		}
	}
	#ÓÊ¼şÏŞÖÆ _E

    &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬ÄúÊäÈëµÄÓÃ»§ÃûÓĞÎÊÌâ£¬Çë²»ÒªÔÚÓÃ»§ÃûÖĞ°üº¬\@\#\$\%\^\*\(\)\+\=\\\{\}\;\'\:\"\,\.\/\<\>\?\[\]\|ÕâÀà×Ö·û£¡") if ($inmembername =~ /[\a\f\n\e\0\r\t\`\~\!\@\#\$\%\^\&\*\(\)\+\=\\\{\}\|\;\'\:\"\,\.\/\<\>\?\[\]]/);
    if($inmembername =~ /_/)  { &error("ÓÃ»§×¢²á&Çë²»ÒªÔÚÓÃ»§ÃûÖĞÊ¹ÓÃÏÂ»®Ïß£¡"); }

    $inmembername =~ s/\&nbsp\;//ig;
    $inmembername =~ s/¡¡/ /g;
    $inmembername =~ s/©¡/ /g;
    $inmembername =~ s/[ ]+/ /g;
    $inmembername =~ s/[ ]+/_/;
    $inmembername =~ s/[_]+/_/;
    $inmembername =~ s/ÿ//isg;
    $inmembername =~ s///isg;
    $inmembername =~ s/¡¡//isg;
    $inmembername =~ s/©¡//isg;
    $inmembername =~ s/()+//isg;
    $inmembername =~ s/[\a\f\n\e\0\r\t\`\~\!\@\#\$\%\^\&\*\(\)\+\=\\\{\}\;\|\'\:\"\,\.\/\<\>\?\[\]]//isg;
    $inmembername =~ s/\s*$//g;
    $inmembername =~ s/^\s*//g;

    &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬ÄúÊäÈëµÄÓÃ»§ÃûÓĞÎÊÌâ£¬Çë¸ü»»Ò»¸ö") if ($inmembername =~ /^q(.+?)-/ig || $inmembername =~ /^q(.+?)q/ig);
    
    $bannedmember = "no";
    open(FILE,"${lbdir}data/banemaillist.cgi");
    my $bannedemail = <FILE>;
    close(FILE);
    chomp $bannedemail;
    $bannedemail = "\t$bannedemail\t";
    $bannedemail =~ s/\t\t/\t/isg;
    my $emailaddresstemp = "\t$emailaddress\t";
    $bannedmember = "yes" if ($bannedemail =~ /$emailaddresstemp/i);

    $filetoopen = "$lbdir" . "data/baniplist.cgi";
    open(FILE,"${lbdir}data/baniplist.cgi");
    my $bannedips = <FILE>;
    close(FILE);
    chomp $bannedips;
    $bannedips = "\t$bannedips\t";
    $bannedips =~ s/\t\t/\t/isg;
    
    (my $ipaddresstemp = $ipaddress) =~ s/\./\\\./g;
    $ipaddresstemp =~ /^((((.*?\\\.).*?\\\.).*?\\\.).*?)$/;
    $bannedmember = "yes" if ($bannedips =~ /\t($1|$2|$3|$4)\t/);

    $bannedmember = "yes" if (($inmembername =~ /^m-/i)||($inmembername =~ /^s-/i)||($inmembername =~ /tr-/i)||($inmembername =~ /^y-/i)||($inmembername =~ /×¢²á/i)||($inmembername =~ /guest/i)||($inmembername =~ /qq-/i)||($inmembername =~ /qq/i)||($inmembername =~ /qw/i)||($inmembername =~ /q-/i)||($inmembername =~ /qx-/i)||($inmembername =~ /qw-/i)||($inmembername =~ /qr-/i)||($inmembername =~ /^È«Ìå/i)||($inmembername =~ /register/i)||($inmembername =~ /³ÏÆ¸ÖĞ/i)||($inmembername =~ /°ßÖñ/i)||($inmembername =~ /¹ÜÀíÏµÍ³Ñ¶Ï¢/i)||($inmembername =~ /leobbs/i)||($inmembername =~ /leoboard/i)||($inmembername =~ /À×°Á/i)||($inmembername =~ /LB5000/i)||($inmembername =~ /È«Ìå¹ÜÀíÈËÔ±/i)||($inmembername =~ /¹ÜÀíÔ±/i)||($inmembername =~ /ÒşÉí/i)||($inmembername =~ /¶ÌÏûÏ¢¹ã²¥/i)||($inmembername =~ /ÔİÊ±¿ÕÈ±/i)||($inmembername =~ /£ª£££¡£¦£ª/i)||($inmembername =~ /°æÖ÷/i)||($inmembername =~ /Ì³Ö÷/i)||($inmembername =~ /nodisplay/i)||($inmembername =~ /^system/i)||($inmembername =~ /---/i)||($inmembername eq "admin")||($inmembername eq "root")||($inmembername eq "copy")||($inmembername =~ /^sub/)||($inmembername =~ /^exec/)||($inmembername =~ /\@ARGV/i)||($inmembername =~ /^require/)||($inmembername =~ /^rename/i)||($inmembername =~ /^dir/i)||($inmembername =~ /^print/i)||($inmembername =~ /^con/i)||($inmembername =~ /^nul/i)||($inmembername =~ /^aux/i)||($inmembername =~ /^com/i)||($inmembername =~ /^lpt/i)||($inmembername =~ /^open/i));

    if ($bannedmember eq "yes") { &error("ÓÃ»§×¢²á&²»ÔÊĞí×¢²á£¬ÄãÌîĞ´µÄÓÃ»§Ãû¡¢Email »òµ±Ç°µÄ IP ±»¹ÜÀí†TÉèÖÃ³É½ûÖ¹×¢²áĞÂÓÃ»§ÁË£¬Çë¸ü»»»òÕßÁªÏµ¹ÜÀí†TÒÔ±ã½â¾ö£¡"); }
    
    open(THEFILE,"${lbdir}data/noreglist.cgi");
    $userarray = <THEFILE>;
    close(THEFILE);
    chomp $userarray;
    @saveduserarray = split(/\t/,$userarray);
    $noreg = "no";
    foreach (@saveduserarray) {
	chomp $_;
	$_ =~ s/\|/\\\|/isg;
	if ($inmembername =~ m/$_/isg) {
	    $noreg = "yes";
	    last;
	}
    }
    &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬ÄãËù×¢²áµÄÓÃ»§ÃûÒÑ¾­±»±£Áô»òÕß±»½ûÖ¹×¢²á£¬Çë¸ü»»Ò»¸öÓÃ»§Ãû£¡") if ($noreg eq "yes");
	
    if (($passwordverification eq "yes") && ($emailfunctions ne "off")) {
        $seed = int(myrand(100000));
        $password = crypt($seed, aun);
        $password =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
        $password =~ s/[^a-zA-Z0-9]//isg;
        $password = substr($password, 4, 8);
    }
        
    if ($interests) {
        $interests =~ s/[\t\r]//g;
        $interests =~ s/  / /g;
        $interests =~ s/\n\n/\<p\>/g;
        $interests =~ s/\n/\<br\>/g;
    }
        
    if ($signature) {
        $signature =~ s/[\t\r]//g;
        $signature =~ s/  / /g;
        $signature =~ s/\n\n/\n\&nbsp;\n/isg;
        $signature =~ s/\n/\[br\]/isg;
        $signature =~ s/\[br\]\[br\]/\[br\]\&nbsp;\[br\]/isg;
	$signature = &dofilter("$signature");
	$signature =~ s/(ev)a(l)/$1&#97;$2/isg;
    }   
    
    my @testsig = split(/\[br\]/,$signature);
    my $siglines = @testsig;
    
    if ($siglines > $maxsignline)           { &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬ÔÚÄúµÄÇ©ÃûÖĞÖ»ÔÊĞíÓĞ $maxsignline ĞĞ£¡"); }
    if (length($signature) > $maxsignlegth) { &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬Ç©Ãû²»ÄÜ³¬¹ı $maxsignlegth ×Ö·û£¡"); }

    my @testins = split(/\<br\>/,$interests);
    my $inslines = @testins;
    if ($inslines > $maxinsline)           { &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬¸öÈË¼ò½éÖ»ÔÊĞíÓĞ $maxinsline ĞĞ£¡"); }
    if (length($interests) > $maxinslegth) { &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬¸öÈË¼ò½é²»ÄÜ³¬¹ı $maxinslegth ×Ö·û£¡"); }

    if (($personalavatar)&&($personalwidth)&&($personalheight)) {
        if ($personalavatar !~ /^http:\/\/[\w\W]+\.[\w\W]+$/) { &error("ÓÃ»§×¢²á&×Ô¶¨ÒåÍ·ÏñµÄ URL µØÖ·ÓĞÎÊÌâ£¡"); }
        if (($personalavatar !~ /\.gif$/isg)&&($personalavatar !~ /\.jpg$/isg)&&($personalavatar !~ /\.png$/isg)&&($personalavatar !~ /\.bmp$/isg)) { &error("ÓÃ»§×¢²á&×Ô¶¨ÒåÍ·Ïñ±ØĞëÎª PNG¡¢GIF »ò JPG ¸ñÊ½") ; }
        if (($personalwidth  < 20)||($personalwidth  > $maxposticonwidth))  { &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬ÄúÌîĞ´µÄ×Ô¶¨ÒåÍ¼Ïñ¿í¶È±ØĞëÔÚ 20 -- $maxposticonwidth ÏñËØÖ®¼ä£¡"); }
        if (($personalheight < 20)||($personalheight > $maxposticonheight)) { &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬ÄúÌîĞ´µÄ×Ô¶¨ÒåÍ¼Ïñ¸ß¶È±ØĞëÔÚ 20 -- $maxposticonheight ÏñËØÖ®¼ä£¡"); }
        $useravatar = "noavatar";
        $personalavatar =~ s/${imagesurl}/\$imagesurl/o;
    }
    else {
    	if ($addme) { $personalavatar=""; } else { $personalavatar=""; $personalwidth=""; $personalheight=""; }
    } #Çå³ı×Ô¶¨ÒåÍ·ÏñĞÅÏ¢

    if($inmembername =~ /\t/) { &error("ÓÃ»§×¢²á&Çë²»ÒªÔÚÓÃ»§ÃûÖĞÊ¹ÓÃÌØÊâ×Ö·û£¡"); }
    if($password =~ /[^a-zA-Z0-9]/)     { &error("ÓÃ»§×¢²á&ÂÛÌ³ÃÜÂëÖ»ÔÊĞí´óĞ¡Ğ´×ÖÄ¸ºÍÊı×ÖµÄ×éºÏ£¡£¡"); }
    if($password =~ /^lEO/)     { &error("ÓÃ»§×¢²á&ÂÛÌ³ÃÜÂë²»ÔÊĞíÊÇ lEO ¿ªÍ·£¬Çë¸ü»»£¡£¡"); }

    $recomm_q = $recommender;
    $recomm_q =~ y/ /_/;
    $recomm_q =~ tr/A-Z/a-z/;
    $member_q = $inmembername;
    $member_q =~ y/ /_/;
    $member_q =~ tr/A-Z/a-z/;
    if ($recomm_q eq $member_q) { &error("ÓÃ»§×¢²á&Äú²»ÄÜÍÆ¼ö×Ô¼º£¡"); }
    
    $tempinmembername =$inmembername;
    $tempinmembername =~ s/ //g;
    $tempinmembername =~ s/¡¡//g;
    if ($tempinmembername eq "")  { &error("ÓÃ»§×¢²á&ÄãµÄÓÃ»§ÃûÓĞµãÎÊÌâÓ´£¬»»Ò»¸ö£¡"); }
    if ($inmembername =~ /^¿ÍÈË/) { &error("ÓÃ»§×¢²á&Çë²»ÒªÔÚÓÃ»§ÃûµÄ¿ªÍ·ÖĞÊ¹ÓÃ¿ÍÈË×ÖÑù£¡"); }
    if (length($inmembername)>12) { &error("ÓÃ»§×¢²á&ÓÃ»§ÃûÌ«³¤£¬Çë²»Òª³¬¹ı12¸ö×Ö·û£¨6¸öºº×Ö£©£¡"); }
    if (length($inmembername)<2)  { &error("ÓÃ»§×¢²á&ÓÃ»§ÃûÌ«¶ÌÁË£¬Çë²»ÒªÉÙì¶2¸ö×Ö·û£¨1¸öºº×Ö£©£¡"); }
    if (length($newlocation)>16)  { &error("ÓÃ»§×¢²á&À´×ÔµØÇø¹ı³¤£¬Çë²»Òª³¬¹ı16¸ö×Ö·û£¨8¸öºº×Ö£©£¡"); }
    
    if (($inmembername =~ m/_/)||(!$inmembername)) { &error("ÓÃ»§×¢²á&ÓÃ»§ÃûÖĞº¬ÓĞ·Ç·¨×Ö·û£¡"); }

    if ($passwordverification eq "no"){
	if ($password ne $password2) { &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬ÄãÊäÈëµÄÁ½´ÎÂÛÌ³ÃÜÂë²»ÏàÍ¬£¡");   }
        if(length($password)<8)      { &error("ÓÃ»§×¢²á&ÂÛÌ³ÃÜÂëÌ«¶ÌÁË£¬Çë¸ü»»£¡ÂÛÌ³ÃÜÂë±ØĞë 8 Î»ÒÔÉÏ£¡"); }
#       if ($password =~ /^[0-9]+$/) { &error("ÓÃ»§×¢²á&ÂÛÌ³ÃÜÂëÇë²»ÒªÈ«²¿ÎªÊı×Ö£¬Çë¸ü»»£¡"); }
    }

    if ($inmembername eq $password) { &error("ÓÃ»§×¢²á&ÇëÎğ½«ÓÃ»§ÃûºÍÂÛÌ³ÃÜÂëÉèÖÃ³ÉÏàÍ¬£¡"); } 

    if($emailaddress !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,4}|[0-9]{1,4})(\]?)$/) { &error("ÓÃ»§×¢²á&ÓÊ¼şµØÖ·´íÎó£¡"); }
    $emailaddress =~ s/[\ \a\f\n\e\0\r\t\`\~\!\$\%\^\&\*\(\)\=\+\\\{\}\;\'\:\"\,\/\<\>\?\|]//isg;
    $homepage =~ s/[\ \a\f\n\e\0\r\t\|\$\@]//isg;
    $homepage =~ s/ARGV//isg;
    $homepage =~ s/system//isg;

    &getmember("$inmembername","no");
    if ($userregistered ne "no") { &error("ÓÃ»§×¢²á&¸ÃÓÃ»§ÒÑ¾­´æÔÚ£¬ÇëÖØĞÂÊäÈëÒ»¸öĞÂµÄÓÃ»§Ãû£¡"); }
    $membercode    = "me";
    
    $memberfiletitle = $inmembername;
    $memberfiletitle =~ y/ /_/;
    $memberfiletitle =~ tr/A-Z/a-z/;
    $memberfiletitletemp = unpack("H*","$memberfiletitle");
if ($addme) {

    my ($filename) = $addme =~ m|([^/:\\]+)$|; #×¢Òâ,»ñÈ¡ÎÄ¼şÃû×ÖµÄĞÎÊ½±ä»¯
    my $fileexp;

    $fileexp =  ($filename =~ /\.jpe?g\s*$/i) ? 'jpg'
	        :($filename =~ /\.gif\s*$/i)  ? 'gif'
		:($filename =~ /\.png\s*$/i)  ? 'png'
		:($filename =~ /\.swf\s*$/i)  ? 'swf'
		:($filename =~ /\.bmp\s*$/i)  ? 'bmp'
		:undef;
    $maxuploadava = 200 if (($maxuploadava eq "")||($maxuploadava < 1));
	
    if (($fileexp eq "swf")&&($flashavatar ne "yes")) { &error("²»Ö§³ÖÄãËùÉÏ´«µÄÍ¼Æ¬£¬ÇëÖØĞÂÑ¡Ôñ£¡&½öÖ§³Ö GIF£¬JPG£¬PNG£¬BMP ÀàĞÍ!"); }
    if (!defined $fileexp) { &error("²»Ö§³ÖÄãËùÉÏ´«µÄÍ¼Æ¬£¬ÇëÖØĞÂÑ¡Ôñ£¡&½öÖ§³Ö GIF£¬JPG£¬PNG£¬BMP£¬SWF ÀàĞÍ!"); }

    my $filesize=0;
    my $buffer;
    open (FILE,">${imagesdir}/usravatars/$memberfiletitletemp.$fileexp");
    binmode (FILE);
    binmode ($addme); #×¢Òâ
    while (((read($addme,$buffer,4096)))&&!($filesize>$maxuploadava)) {
	print FILE $buffer;
	$filesize=$filesize+4;
    }
    close (FILE);
    close ($addme);

    if ($fileexp eq "gif"||$fileexp eq "jpg"||$fileexp eq "bmp"||$fileexp eq "jpeg"||$fileexp eq "png") {
      eval("use Image::Info qw(image_info);"); 
      if ($@ eq "") { 
        my $info = image_info("${imagesdir}usravatars/$memberfiletitletemp.$fileexp");
	if ($info->{error} eq "Unrecognized file format"){
            unlink ("${imagesdir}usravatars/$memberfiletitletemp.$fileexp");
            &error("ÉÏ´«³ö´í&ÉÏ´«ÎÄ¼ş²»ÊÇÍ¼Æ¬ÎÄ¼ş£¬ÇëÉÏ´«±ê×¼µÄÍ¼Æ¬ÎÄ¼ş£¡");
        }
            if ($personalwidth eq "" || $personalwidth eq 0) {
            	if ($info->{width} ne "") { $personalwidth = $info->{width}; }
            	elsif ($info->{ExifImageWidth} ne "") { $personalwidth = $info->{ExifImageWidth}; }
            }
            if ($personalheight eq "" || $personalheight eq 0) {
            	if ($info->{height} ne "") { $personalheight = $info->{height}; }
            	elsif ($info->{ExifImageLength} ne "") { $personalheight = $info->{ExifImageLength}; }
            }
        undef $info;
      }
    }
    if ($filesize>$maxuploadava) {
        unlink ("${imagesdir}usravatars/$memberfiletitletemp.$fileexp");
	&error("ÉÏ´«³ö´í&ÉÏ´«ÎÄ¼ş´óĞ¡³¬¹ı$maxuploadava£¬ÇëÖØĞÂÑ¡Ôñ£¡");
    }

    if (($personalwidth  < 20)||($personalwidth  > $maxposticonwidth))  { &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬ÄúÌîĞ´µÄ×Ô¶¨ÒåÍ¼Ïñ¿í¶È($personalwidth)±ØĞëÔÚ 20 -- $maxposticonwidth ÏñËØÖ®¼ä£¡"); }
    if (($personalheight < 20)||($personalheight > $maxposticonheight)) { &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬ÄúÌîĞ´µÄ×Ô¶¨ÒåÍ¼Ïñ¸ß¶È($personalheight)±ØĞëÔÚ 20 -- $maxposticonheight ÏñËØÖ®¼ä£¡"); }

    $useravatar="noavatar";
    $personalavatar="\$imagesurl/usravatars/$memberfiletitletemp.$fileexp";
}
    if ($useverify eq "yes") {
        &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬ÄãÊäÈëµÄĞ£ÑéÂëÓĞÎÊÌâ»òÕßÒÑ¾­¹ıÆÚ£¡") if (&checkverify);
    }

    $regcontrollimit = 30 if (($regcontrollimit eq "")||($regcontrollimit < 0 ));
    $regcontrol = 0;

    $filetoopen = "$lbdir" . "data/lastregtime.cgi";
    if (-e "$filetoopen") {
	open(FILE,"$filetoopen");
	my $lastfiledate = <FILE>;
        close(FILE);
        chomp $lastfiledate;
        my ($lastregtime,$lastregip) = split(/\|/,$lastfiledate);
        $lastregtime = $lastregtime + $regcontrollimit;
        if (($lastregtime > $joineddate)&&($ipaddress eq $lastregip)) { $regcontrol = 1; }
    }
    open(FILE,">$filetoopen");
    print FILE "$joineddate|$ipaddress";
    close(FILE);
        
    if ($regcontrol eq 1) { &error("ÓÃ»§×¢²á&¶Ô²»Æğ£¬Äú±ØĞëµÈ´ı $regcontrollimit ÃëÖÓ²ÅÄÜÔÙ´Î×¢²á£¡"); }

    if ($adminverification eq "yes") {
	$emailaddress1 = $emailaddress;
        $emailaddress  = $adminemail_out;
    }

if ($password ne "") {
    $notmd5password = $password;
    eval {$password = md5_hex($password);};
    if ($@) {eval('use Digest::MD5 qw(md5_hex);$password = md5_hex($password);');}
    unless ($@) {$password = "lEO$password";}
}
else {
    $notmd5password = $password;
}

    $signature=~s/\n/<br>/g; 
    require "dosignlbcode.pl";
    $signature1=&signlbcode($signature); 
    $signature=$signature."aShDFSiod".$signature1; 
    mkdir ("${lbdir}$memdir/old", 0777) if (!(-e "${lbdir}$memdir/old"));
    chmod(0777,"${lbdir}$memdir/old");
    my $namenumber = &getnamenumber($memberfiletitle);
    $filetomake = "$lbdir" . "$memdir/$namenumber/$memberfiletitle.cgi";
    if (open(FILE, ">$filetomake")) {
        print FILE "$inmembername\t$password\t$membertitle\t$membercode\t$numberofposts\t$emailaddress\t$showemail\t$ipaddress\t$homepage\t$oicqnumber\t$icqnumber\t$newlocation\t$interests\t$joineddate\t$lastpostdate\t$signature\t$timedifference\t\t$useravatar\t$userflag\t$userxz\t$usersx\t$personalavatar\t$personalwidth\t$personalheight\t0\t$lastgone\t1\t$useradd04\t$useradd02\t$mymoney\t0\t$sex\t$education\t$marry\t$work\t$born\t\t\t\t\t\t\t$userquestion\t\t$jifen\t\t$soccerdata\t0\t";
        close(FILE);
    }
    $filetomake = "$lbdir" . "$memdir/old/$memberfiletitle.cgi";
    if (open(FILE, ">$filetomake")) {
        print FILE "$inmembername\t$password\t$membertitle\t$membercode\t$numberofposts\t$emailaddress\t$showemail\t$ipaddress\t$homepage\t$oicqnumber\t$icqnumber\t$newlocation\t$interests\t$joineddate\t$lastpostdate\t$signature\t$timedifference\t\t$useravatar\t$userflag\t$userxz\t$usersx\t$personalavatar\t$personalwidth\t$personalheight\t0\t$lastgone\t1\t$useradd04\t$useradd02\t$mymoney\t0\t$sex\t$education\t$marry\t$work\t$born\t\t\t\t\t\t\t$userquestion\t\t$jifen\t\t$soccerdata\t0\t";
        close(FILE);
    }

    if (($recommender ne "") && ($recomm_q ne $member_q)) {
        $recomm_q = &stripMETA($recomm_q);
	$namenumber = &getnamenumber($recomm_q);
	&checkmemfile($recomm_q,$namenumber);
        my $filetoopen = "${lbdir}$memdir/$namenumber/$recomm_q.cgi";
        if (-e $filetoopen) { &recommfunc("$recommender");  $recommfuncerror = ""; }
                       else { $recommfuncerror = " (×¢Òâ£ºÍÆ¼öÈËÓÃ»§Ãû²»´æÔÚ£¡)"; }
    }

    $filetomakeopen = "${lbdir}data/lbmember.cgi";
    if (open (MEMFILE, ">>$filetomakeopen")) {
	print MEMFILE "$inmembername\t$membercode\t0\t$joineddate\t$emailaddress\t\n";
	close (MEMFILE);
    }

   $filetomakeopen = "${lbdir}data/lbemail/$charone.cgi";
   if (open (MEMFILE, ">>$filetomakeopen")) {
	print MEMFILE "$emailaddress\t$inmembername\n";
	close (MEMFILE);
   }

    if (($born ne "")&&($born ne "//")) {
	$filetomakeopen = "${lbdir}data/lbmember3.cgi";
	if (open (MEMFILE, ">>$filetomakeopen")) {
	    print MEMFILE "$inmembername\t$born\t\n";
	    close (MEMFILE);
	}
	$month = int($month);
	if (open (MEMFILE, ">>${lbdir}calendar/borninfo$month.cgi")) {
	    print MEMFILE "$inmembername\t$born\t\n";
	    close (MEMFILE);
	}
    }

    $filetomakeopen = "${lbdir}data/lbmember4.cgi";
    if (open (MEMFILE, ">>$filetomakeopen")) {
	print MEMFILE "$inmembername\t$ipaddress\t\n";
	close (MEMFILE);
    }

    $inmembername =~ y/_/ /;
    $inmemberfile = $inmembername;
    $inmemberfile =~ y/ /_/;
    $inmemberfile =~ tr/A-Z/a-z/;
    $currenttime = time ;
    if ($sendwelcomemessage ne "no" && $allowusemsg ne "off") {
        $filetoopen = "$lbdir" . "data/newusrmsg.dat";
	open(FILE,$filetoopen);
	sysread(FILE, $tempoutput,(stat(FILE))[7]);
    	close(FILE);
        $tempoutput =~ s/\r//isg;

	$tempoutput =~ s/\n//;

        $filetoopen = "$lbdir". "$msgdir/in/$inmemberfile" . "_msg.cgi";
        if (open (FILE, ">$filetoopen")) {
            print FILE "£ª£££¡£¦£ªÈ«Ìå¹ÜÀíÈËÔ±\tno\t$currenttime\t»¶Ó­Äú·ÃÎÊ$boardname£¬×£ÄãÊ¹ÓÃÓä¿ì£¡\t$tempoutput<BR><BR>----------------------------<BR>LeoBBS ÓÉÀ×°Á¿Æ¼¼ÈÙÓş³öÆ·<BR>Ö÷Ò³:<a href=http://www.LeoBBS.com target=_blank>http://www.LeoBBS.com</a>\n";
            close (FILE);
        }
    }
    ###·¢ËÍ×¢²áĞÅ¼ş
    if  (($passwordverification eq "no") && ($emailfunctions ne "off")) {
	$to = $emailaddress;
        $from = $adminemail_out;
	$subject = "¸ĞĞ»ÄúÔÚ$boardnameÖĞ×¢²á£¡";              
        $message .= "\n»¶Ó­Äã¼ÓÈë$boardname! <br>\n";
        $message .= "ÂÛÌ³URL: $boardurl/leobbs.cgi\n <br><br>\n <br>\n";
        $message .= "------------------------------------<br>\n";
        $message .= "ÄúµÄÓÃ»§Ãû¡¢ÂÛÌ³ÃÜÂëÈçÏÂ¡£\n <br>\n";
        $message .= "ÓÃ»§Ãû£º $inmembername <br>\n";
        $message .= "ÂÛÌ³ÃÜÂë£º $notmd5password\n <br><br>\n <br>\n";
        $message .= "Òª×¢ÒâÂÛÌ³ÃÜÂëÊÇÇø·Ö´óĞ¡Ğ´µÄ\n <br>\n";
        $message .= "ÄúËæÊ±¿ÉÒÔÊ¹ÓÃÓÃ»§×ÊÁÏĞŞ¸ÄÄúµÄÂÛÌ³ÃÜÂë <br>\n";
        $message .= "Èç¹ûÄú¸Ä±äÁËÄúµÄÓÊ¼şµØÖ·£¬ <br>\n";
        $message .= "½«»áÓĞÒ»¸öĞÂµÄÂÛÌ³ÃÜÂë¼Ä¸øÄú¡£\n <br><br>\n";
        $message .= "------------------------------------<br>\n";      
        &sendmail($from, $from, $to, $subject, $message);
    }
    ####·¢ËÍ×¢²áĞÅ¼ş½áÊø
  
    if (($passwordverification eq "yes") && ($emailfunctions ne "off")) {
	$namecookie = cookie(-name => "amembernamecookie", -value => "", -path => "$cookiepath/", -expires => "now");
	$passcookie = cookie(-name => "apasswordcookie"  , -value => "", -path => "$cookiepath/", -expires => "now");

	if ($adminverification eq "yes") {
	    $to = $adminemail_out;
	    $from = $emailaddress;
	    $subject = "µÈ´ıÄúÈÏÖ¤$boardnameÖĞµÄ×¢²á£¡";
	    $message .= "\n»¶Ó­Äã¼ÓÈë$boardname£¡\n";
	    $message .= "ÂÛÌ³URL:$boardurl/leobbs.cgi\n\n\n";
	    $message .= "------------------------------------\n";
	    $message .= "ÄúµÄÓÃ»§Ãû¡¢ÂÛÌ³ÃÜÂëÈçÏÂ¡£\n\n";
	    $message .= "ÓÃ»§Ãû£º $inmembername\n";
	    $message .= "ÂÛÌ³ÃÜÂë£º $notmd5password\n\n\n";
	    $message .= "ÓÊ  Ïä£º $emailaddress1\n\n\n";
	    $message .= "ÂÛÌ³ÃÜÂëÊÇÇø·Ö´óĞ¡Ğ´µÄ\n\n";
	    $message .= "ÇëÁ¢¼´µÇÂ¼²¢ĞŞ¸ÄĞÅÏä(ÏÖÔÚĞÅÏäÊÇ¹ÜÀíÔ±µÄ\n";
	    $message .= "ĞÅÏä)£¬½«»áÓĞĞÂµÄÂÛÌ³ÃÜÂëÖ±½Ó¼Ä¸øÄú¡£\n\n";
	    $message .= "------------------------------------\n";
	    $message .= "Çë»Ø¸´»ò×ª·¢ÈÏÖ¤¸Ã»áÔ±£¬²¢ÒªÇóÆäĞŞ¸ÄĞÅÏä£¡\n";
	} else {
	    $to = $emailaddress;
	    $from = $adminemail_out;
	    $subject = "¸ĞĞ»ÄúÔÚ$boardnameÖĞ×¢²á£¡";
	    $message .= "\n»¶Ó­Äã¼ÓÈë$boardname£¡<br>\n";
	    $message .= "ÂÛÌ³URL:$boardurl/leobbs.cgi\n <br><br>\n <br>\n";
	    $message .= "------------------------------------<br>\n";
	    $message .= "ÄúµÄÓÃ»§Ãû¡¢ÂÛÌ³ÃÜÂëÈçÏÂ¡£\n<br><br>\n";
            $message .= "ÓÃ»§Ãû£º $inmembername <br>\n";
	    $message .= "ÂÛÌ³ÃÜÂë£º $notmd5password\n <br><br>\n<br>\n";
	    $message .= "ÂÛÌ³ÃÜÂëÊÇÇø·Ö´óĞ¡Ğ´µÄ \n<br><br>\n";
	    $message .= "ÄúËæÊ±¿ÉÒÔÊ¹ÓÃÓÃ»§×ÊÁÏĞŞ¸ÄÄúµÄÂÛÌ³ÃÜÂë <br>\n";
	    $message .= "Èç¹ûÄú¸Ä±äÁËÄúµÄÓÊ¼şµØÖ·£¬ <br>\n";
	    $message .= "½«»áÓĞÒ»¸öĞÂµÄÂÛÌ³ÃÜÂë¼Ä¸øÄú¡£ <br><br>\n\n";
	    $message .= "------------------------------------<br>\n";
	}
	&sendmail($from, $from, $to, $subject, $message);
    }

    if ($newusernotify eq "yes" && $emailfunctions ne "off") {
	$to = $adminemail_in;
	$from = $adminemail_out;
	$subject = "$boardnameÓĞĞÂÓÃ»§×¢²áÁË£¡";
	$message = "\nÂÛÌ³£º$boardname <br>\n";
	$message .= "ÂÛÌ³URL:$boardurl/leobbs.cgi <br>\n";
	$message .= "-------------------------------------\n<br><br>\n";
	$message .= "ĞÂÓÃ»§×¢²áµÄĞÅÏ¢ÈçÏÂ¡£ <br><br>\n\n";
	$message .= "ÓÃ»§Ãû£º $inmembername <br>\n";
	$message .= "ÃÜ  Âë£º $notmd5password <br>\n";
	$message .= "ÓÊ  ¼ş£º $emailaddress <br>\n";
	$message .= "Ö÷  Ò³£º $homepage <br>\n";
	$message .= "IPµØÖ·£º $ipaddress\n <br><br>\n";
	$message .= "ÍÆ¼öÈË£º $recommender\n <br><br>\n" if ($recommender ne "");
	$message .= "------------------------------------<br>\n";
	&sendmail($from, $from, $to, $subject, $message);
    }

    if ($inforum eq "") { $refrashurl = "leobbs.cgi"; } else { $refrashurl = "forums.cgi?forum=$inforum"; }
    $output .= qq~<tr>
	<td bgcolor=$titlecolor $catbackpic valign=middle align=center><font color=$fontcolormisc><b>¸ĞĞ»Äú×¢²á£¬$inmembername</b>$recommfuncerror</font></td></tr><tr>
        <td bgcolor=$miscbackone valign=middle><font color=$fontcolormisc>¾ßÌåÇé¿ö£º<ul><li><a href="$refrashurl">°´´Ë·µ»ØÂÛÌ³</a>
        <meta http-equiv="refresh" content="3; url=$refrashurl">
	</ul></tr></td></table></td></tr></table><SCRIPT>valignend()</SCRIPT>~;

    if (($passwordverification eq "yes") && ($emailfunctions ne "off")) { $output =~ s/°´´Ë·µ»ØÂÛÌ³/ÄúµÄÂÛÌ³ÃÜÂëÒÑ¾­¼Ä³ö£¬°´´Ë·µ»ØÂÛÌ³£¬È»ºóÊ¹ÓÃÓÊ¼şÖĞµÄÃÜÂëµÇÂ¼/; }
    else {
        $namecookie = cookie(-name => "amembernamecookie", -value => "$inmembername", -path => "$cookiepath/", -expires => "+30d");
        $passcookie = cookie(-name => "apasswordcookie"  , -value => "$password"    , -path => "$cookiepath/", -expires => "+30d");
    }
    require "$lbdir" . "data/boardstats.cgi";
    $filetomake = "$lbdir" . "data/boardstats.cgi";
    my $filetoopens = &lockfilename($filetomake);
    if (!(-e "$filetoopens.lck")) {
	$totalmembers++;
	&winlock($filetomake) if ($OS_USED eq "Nt");
	if (open(FILE, ">$filetomake")) {
	    flock(FILE, 2) if ($OS_USED eq "Unix");
	    print FILE "\$lastregisteredmember = \'$inmembername\'\;\n";
	    print FILE "\$totalmembers = \'$totalmembers\'\;\n";
	    print FILE "\$totalthreads = \'$totalthreads\'\;\n";
	    print FILE "\$totalposts = \'$totalposts\'\;\n";
	    print FILE "\n1\;";
	    close (FILE);
	}
	&winunlock($filetomake) if ($OS_USED eq "Nt");
    }
    else {
    	unlink ("$filetoopens.lck") if ((-M "$filetoopens.lck") *86400 > 30);
    }
}
elsif ($action eq "agreed") {
require "cleanolddata.pl";
&cleanolddata1;
    if (($passwordverification eq "yes") && ($emailfunctions ne "off")) {
	if ($adminverification eq "yes") {
	    $requirepass = qq~<tr><td bgcolor=$miscbackone colspan=2 align=center><font color=$fontcolormisc><b>ÄúµÄÂÛÌ³ÃÜÂë½«Í¨¹ıÓÊ¼ş¼Ä¸ø¹ÜÀíÔ±£¬ÔÚ¾­¹ı¹ÜÀíÔ±ÈÏÖ¤ºó½«³ĞÈÏÄãµÄ×¢²á£¡</td></tr>~;
        } else {
    	    $requirepass = qq~<tr><td bgcolor=$miscbackone colspan=2 align=center><font color=$fontcolormisc><b>ÄúµÄÂÛÌ³ÃÜÂë½«Í¨¹ıÓÊ¼ş¼Ä¸øÄú<BR>Èç¹ûÄãÒ»Ö±Ã»ÓĞÊÕµ½ÓÊ¼ş£¬ÄÇÃ´Çë¼ì²é×¢²áĞÅÊÇ·ñ±»·Åµ½ÁËÀ¬»øÏäÄÚÁË£¡</td></tr>~;
	}
	$qa=qq~~;
    } else {
        $requirepass = qq~<tr>
        <td bgcolor=$miscbackone width=40%><font color=$fontcolormisc><b>ÂÛÌ³ÃÜÂë£º (ÖÁÉÙ8Î»)</b><br>ÇëÊäÈëÂÛÌ³ÃÜÂë£¬Çø·Ö´óĞ¡Ğ´<br>Ö»ÄÜÊ¹ÓÃ´óĞ¡Ğ´×ÖÄ¸ºÍÊı×ÖµÄ×éºÏ</td>
        <td bgcolor=$miscbackone width=60%><input type=password name="password" maxlength=20>&nbsp;* ´ËÏî±ØĞëÌîĞ´</td>
        </tr><tr>
        <td bgcolor=$miscbackone><font color=$fontcolormisc><b>ÂÛÌ³ÃÜÂë£º (ÖÁÉÙ8Î»)</b><br>ÔÙÊäÒ»±é£¬ÒÔ±ãÈ·¶¨£¡</td>
        <td bgcolor=$miscbackone><input type=password name="password2" maxlength=20>&nbsp;* ´ËÏî±ØĞëÌîĞ´</td>
        </tr>~;
        $qa=qq~<tr><td bgcolor=$miscbackone><font color=$fontcolormisc><b>ÂÛÌ³ÃÜÂëÌáÊ¾ÎÊÌâ£º</b>ÓÃÓÚÈ¡µÃÍü¼ÇÁËµÄÂÛÌ³ÃÜÂë<br>×î´ó 20 ¸ö×Ö½Ú£¨10¸öºº×Ö£©</td> 
<td bgcolor=$miscbackone><input type=text name="getpassq" value="" size=20 maxlength=20></td></tr>
<tr><td bgcolor=$miscbackone><font color=$fontcolormisc><b>ÂÛÌ³ÃÜÂëÌáÊ¾´ğ°¸£º</b>ÅäºÏÉÏÀ¸Ê¹ÓÃ<br>×î´ó 20 ¸ö×Ö½Ú£¨10¸öºº×Ö£©</td> 
<td bgcolor=$miscbackone><input type=text name="getpassa" value="" size=20 maxlength=20></td></tr>~;
	$passcheck = qq~	if (document.creator.password.value == '')
	{
		window.alert('Äú»¹Ã»ÓĞÊäÈëÄúµÄÃÜÂë£¡');
		document.creator.password.focus();
		return false;
	}
	if (document.creator.password.value != document.creator.password2.value)
	{
		window.alert('Á½´ÎÊäÈëµÄÃÜÂë²»Ò»ÖÂ£¡');
		document.creator.password.focus();
		return false;
	}
	if (document.creator.password.value.length < 8)
	{
		window.alert('ÃÜÂëÌ«¶ÌÁË£¬Çë¸ü»»£¡ÃÜÂë±ØĞë 8 Î»ÒÔÉÏ£¡');
		document.creator.password.focus();
		return false;
	}~;
    }

    if ($avatars eq "on") {
	if ($arrowavaupload eq "on") { $avaupload = qq~<br>ÉÏ´«Í·Ïñ£º <input type="file" size=20 name="addme">¡¡ÉÏ´«×Ô¶¨ÒåÍ·Ïñ¡£<br>~;} else { undef $avaupload; }
        open (FILE, "${lbdir}data/lbava.cgi");
	sysread(FILE, $totleavator,(stat(FILE))[7]);
        close (FILE);
        $totleavator =~ s/\r//isg;
        my @images = split (/\n/, $totleavator);
        $totleavator = @images -1;
        $selecthtml .= qq~<option value="noavatar" selected>²»ÒªÍ·Ïñ</option>\n~;
        $currentface = "noavatar";

        foreach (@images) {
            $_ =~ s/\.(gif|jpg)$//i;
            next if ($_ =~ /admin_/);
            if ($_ ne "noavatar") { $selecthtml .= qq~<option value="$_">$_</option>\n~; }
        }

        $avatarhtml = qq~<script language="javascript">
function showimage(){document.images.useravatars.src="$imagesurl/avatars/"+document.creator.useravatar.options[document.creator.useravatar.selectedIndex].value+".gif";}
</script>
<tr><td bgcolor=$miscbackone valign=top><font color=$fontcolormisc><b>¸öĞÔÍ¼Æ¬£º</b><br>Äú¿ÉÒÔÑ¡ÔñÒ»¸ö¸öĞÔÍ¼Æ¬£¬µ±Äã·¢±íÊ±½«ÏÔÊ¾ÔÚÄúµÄÃû×ÖÏÂ·½¡£<BR>Èç¹ûÄãÌîĞ´ÁËÏÂÃæµÄ×Ô¶¨ÒåÍ·Ïñ²¿·Ö£¬ÄÇÃ´ÄãµÄÍ·ÏñÒÔ×Ô¶¨ÒåµÄÎª×¼¡£·ñÔò£¬ÇëÄãÁô¿Õ×Ô¶¨ÒåÍ·ÏñµÄËùÓĞÀ¸Ä¿£¡<BR>
<br><br><b>¹ØÓÚ×Ô¶¨ÒåÍ·Ïñ</b>£º<br>ÄãÒ²¿ÉÒÔÔÚÕâÀï¸ø³öÄã×Ô¶¨ÒåÍ·ÏñµÄ URL µØÖ·£¬Í·ÏñµÄ¸ß¶ÈºÍ¿í¶È(ÏñËØ)¡£ Èç¹û²»ÏëÒª×Ô¶¨ÒåÍ·Ïñ£¬Çë½«ÏàÓ¦À¸Ä¿È«²¿Áô¿Õ£¡<BR>Èç¹û²»ÌîĞ´Í·ÏñµÄ¸ß¶ÈºÍ¿í¶È£¬ÔòÏµÍ³½«×Ô¶¯ÅĞ¶Ï²¢ÌîÈë¡£<BR><BR>
<br><b>Èç¹ûÄã²»ÏëÒªÈÎºÎµÄÍ·Ïñ£¬ÄÇÃ´ÇëÊ×ÏÈÔÚ²Ëµ¥ÉÏÑ¡¡°²»ÒªÍ·Ïñ¡±£¬È»ºóÁô¿ÕËùÓĞ×Ô¶¨ÒåÍ·ÏñµÄ²¿·Ö£¡</b><BR><br>
<td bgcolor=$miscbackone valign=top>×ÜÍ·Ïñ¸öÊı£º $totleavator ¸ö¡£¡¡<a href=viewavatars.cgi target=_blank><B>°´´Ë²é¿´</B></a>ËùÓĞÍ·ÏñÃû³ÆÁĞ±í¡£<BR>
<select name="useravatar" size=1 onChange="showimage()">
$selecthtml
</select>
<img src=$imagesurl/avatars/$currentface.gif name="useravatars" width=32 height=32 hspace=15><br><br><br>
$avaupload
<br>Í¼ÏñÎ»ÖÃ£º <input type=text name="personalavatar" size=20 value="">¡¡ÊäÈëÍêÕûµÄ URL Â·¾¶¡£<br>
<br>Í¼Ïñ¿í¶È£º <input type=text name="personalwidth" size=2 maxlength=3 value=32>¡¡±ØĞëÊÇ 20 -- $maxposticonwidth Ö®¼äµÄÒ»¸öÕûÊı¡£<br>
<br>Í¼Ïñ¸ß¶È£º <input type=text name="personalheight" size=2 maxlength=3 value=32>¡¡±ØĞëÊÇ 20 -- $maxposticonheight Ö®¼äµÄÒ»¸öÕûÊı¡£<br></td>
</td></tr>~;
    }

    $flaghtml = qq~<script language="javascript">
function showflag(){document.images.userflags.src="$imagesurl/flags/"+document.creator.userflag.options[document.creator.userflag.selectedIndex].value+".gif";}
</script>
<tr><td bgcolor=$miscbackone valign=top><font face=$font color=$fontcolormisc><b>ËùÔÚ¹ú¼Ò:</b><br>ÇëÑ¡ÔñÄãËùÔÚµÄ¹ú¼Ò¡£</td>
<td bgcolor=$miscbackone>
<select name="userflag" size=1 onChange="showflag()">
<option value="blank" selected>±£ÃÜ</option>
<option value="China">ÖĞ¹ú</option>
<option value="Angola">°²¸çÀ­</option>
<option value="Antigua">°²Ìá¹Ï</option>
<option value="Argentina">°¢¸ùÍ¢</option>
<option value="Armenia">ÑÇÃÀÄáÑÇ</option>
<option value="Australia">°Ä´óÀûÑÇ</option>
<option value="Austria">°ÂµØÀû</option>
<option value="Bahamas">°Í¹şÂí</option>
<option value="Bahrain">°ÍÁÖ</option>
<option value="Bangladesh">ÃÏ¼ÓÀ­</option>
<option value="Barbados">°Í°Í¶àË¹</option>
<option value="Belgium">±ÈÀûÊ±</option>
<option value="Bermuda">°ÙÄ½´ó</option>
<option value="Bolivia">²£ÀûÎ¬ÑÇ</option>
<option value="Brazil">°ÍÎ÷</option>
<option value="Brunei">ÎÄÀ³</option>
<option value="Canada">¼ÓÄÃ´ó</option>
<option value="Chile">ÖÇÀû</option>
<option value="Colombia">¸çÂ×±ÈÑÇ</option>
<option value="Croatia">¿ËÂŞµØÑÇ</option>
<option value="Cuba">¹Å°Í</option>
<option value="Cyprus">ÈûÆÖÂ·Ë¹</option>
<option value="Czech_Republic">½İ¿Ë</option>
<option value="Denmark">µ¤Âó</option>
<option value="Dominican_Republic">¶àÃ×Äá¼Ó</option>
<option value="Ecuador">¶ò¹Ï¶à¶û</option>
<option value="Egypt">°£¼°</option>
<option value="Estonia">°®É³ÄáÑÇ</option>
<option value="Finland">·ÒÀ¼</option>
<option value="France">·¨¹ú</option>
<option value="Germany">µÂ¹ú</option>
<option value="Great_Britain">Ó¢¹ú</option>
<option value="Greece">Ï£À°</option>
<option value="Guatemala">Î£µØÂíÀ­</option>
<option value="Honduras">ºé¶¼À­Ë¹</option>
<option value="Hungary">ĞÙÑÀÀû</option>
<option value="Iceland">±ùµº</option>
<option value="India">Ó¡¶È</option>
<option value="Indonesia">Ó¡¶ÈÄáÎ÷ÑÇ</option>
<option value="Iran">ÒÁÀÊ</option>
<option value="Iraq">ÒÁÀ­¿Ë</option>
<option value="Ireland">°®¶ûÀ¼</option>
<option value="Israel">ÒÔÉ«ÁĞ</option>
<option value="Italy">Òâ´óÀû</option>
<option value="Jamaica">ÑÀÂò¼Ó</option>
<option value="Japan">ÈÕ±¾</option>
<option value="Jordan">Ô¼µ©</option>
<option value="Kazakstan">¹şÈø¿Ë</option>
<option value="Kenya">¿ÏÄáÑÇ</option>
<option value="Kuwait">¿ÆÍşÌØ</option>
<option value="Latvia">À­ÍÑÎ¬ÑÇ</option>
<option value="Lebanon">Àè°ÍÄÛ</option>
<option value="Lithuania">Á¢ÌÕÍğ</option>
<option value="Malaysia">ÂíÀ´Î÷ÑÇ</option>
<option value="Malawi">ÂíÀ­Î¬</option>
<option value="Malta">Âí¶úËû</option>
<option value="Mauritius">Ã«ÀïÇóË¹</option>
<option value="Morocco">Ä¦Âå¸ç</option>
<option value="Mozambique">ÄªÉ£±È¿Ë</option>
<option value="Netherlands">ºÉÀ¼</option>
<option value="New_Zealand">ĞÂÎ÷À¼</option>
<option value="Nicaragua">Äá¼ÓÀ­¹Ï</option>
<option value="Nigeria">ÄáÈÕÀûÑÇ</option>
<option value="Norway">Å²Íş</option>
<option value="Pakistan">°Í»ùË¹Ì¹</option>
<option value="Panama">°ÍÄÃÂí</option>
<option value="Paraguay">°ÍÀ­¹ç</option>
<option value="Peru">ÃØÂ³</option>
<option value="Poland">²¨À¼</option>
<option value="Portugal">ÆÏÌÑÑÀ</option>
<option value="Romania">ÂŞÂíÄáÑÇ</option>
<option value="Russia">¶íÂŞË¹</option>
<option value="Saudi_Arabia">É³ÌØ°¢À­²®</option>
<option value="Singapore">ĞÂ¼ÓÆÂ</option>
<option value="Slovakia">Ë¹Âå·¥¿Ë</option>
<option value="Slovenia">Ë¹ÂåÎÄÄáÑÇ</option>
<option value="Solomon_Islands">ËùÂŞÃÅ</option>
<option value="Somalia">Ë÷ÂíÀï</option>
<option value="South_Africa">ÄÏ·Ç</option>
<option value="South_Korea">º«¹ú</option>
<option value="Spain">Î÷°àÑÀ</option>
<option value="Sri_Lanka">Ó¡¶È</option>
<option value="Surinam">ËÕÀïÄÏ</option>
<option value="Sweden">Èğµä</option>
<option value="Switzerland">ÈğÊ¿</option>
<option value="Thailand">Ì©¹ú</option>
<option value="Trinidad_Tobago">¶à°Í¸ç</option>
<option value="Turkey">ÍÁ¶úÆä</option>
<option value="Ukraine">ÎÚ¿ËÀ¼</option>
<option value="United_Arab_Emirates">°¢À­²®ÁªºÏÇõ³¤¹ú</option>
<option value="United_States">ÃÀ¹ú</option>
<option value="Uruguay">ÎÚÀ­¹ç</option>
<option value="Venezuela">Î¯ÄÚÈğÀ­</option>
<option value="Yugoslavia">ÄÏË¹À­·ò</option>
<option value="Zambia">ÔŞ±ÈÑÇ</option>
<option value="Zimbabwe">½ò°Í²¼Î¤</option>
</select>
<img src="$imagesurl/flags/blank.gif" name="userflags" border=0 height=14 width=21>
</td></tr>~;

if ($useverify eq "yes") {

    if ($verifyusegd ne "no") {
	eval ('use GD;');
	if ($@) {
            $verifyusegd = "no";
        }
    }
    if ($verifyusegd eq "no") {
	$houzhui = "bmp";
    } else {
	$houzhui = "png";
    }

    require 'verifynum.cgi';
    $venumcheck = qq~
    	if (document.creator.verifynum.value.length < 4)
	{
		window.alert('ÇëÊäÈëÕıÈ·µÄĞ£ÑéÂë£¡');
		return false;
	}
    ~;
}
    $output .= qq~<script>
function Check(){
var Name=document.creator.inmembername.value;
window.open("./checkname.cgi?name="+Name,"Check","width=200,height=20,status=0,scrollbars=0,resizable=1,menubar=0,toolbar=0,location=0");
}
function CheckInput()
{
	if (document.creator.inmembername.value == '')
	{
		window.alert('Äú»¹Ã»ÓĞÌîĞ´ÓÃ»§ÃûÄØ£¿');
		document.creator.inmembername.focus();
		return false;
	}
	if (document.creator.inmembername.value.length > 12)
	{
		window.alert('ÄúµÄÓÃ»§ÃûÌ«³¤ÁË£¬Çë²»Òª¶àÓÚ12¸ö×Ö·û£¨6¸öºº×Ö£©£¡');
		document.creator.inmembername.focus();
		return false;
	}

$passcheck

	var s = document.creator.emailaddress.value;
	if (s.length > 50)
	{
		window.alert('EmailµØÖ·³¤¶È²»ÄÜ³¬¹ı50Î»!');
		return false;
	}

$venumcheck;
	return true;
}
</script>

<form action="$thisprog" method=post name="creator" enctype="multipart/form-data" OnSubmit="return CheckInput()"><tr>
<input type=hidden name="forum" value="$inforum">
<td bgcolor=$miscbacktwo width=40%><font color=$fontcolormisc><b>ÓÃ»§Ãû£º</b><br>×¢²áÓÃ»§Ãû²»ÄÜ³¬¹ı12¸ö×Ö·û£¨6¸öºº×Ö£©</td>
<td bgcolor=$miscbacktwo width=60%><input type=text maxlength="12" name="inmembername">&nbsp;<input onClick="javascript:Check()" type=button value="¼ì²âÕÊºÅ" name="button" class="button">&nbsp;* ´ËÏî±ØĞëÌîĞ´</td>
</tr>$requirepass
<tr><td bgcolor=$miscbacktwo><font color=$fontcolormisc><b>ÓÊ¼şµØÖ·£º</b><br>ÇëÊäÈëÓĞĞ§µÄÓÊ¼şµØÖ·£¬Õâ½«Ê¹ÄúÄÜÓÃµ½ÂÛÌ³ÖĞµÄËùÓĞ¹¦ÄÜ</td>
<td bgcolor=$miscbacktwo><input type=text name="emailaddress">&nbsp;* ´ËÏî±ØĞëÌîĞ´</td></tr>
~;

#	var regu = "^(([0-9a-zA-Z]+)|([0-9a-zA-Z]+[_.0-9a-zA-Z-]*[0-9a-zA-Z]+))\@([a-zA-Z0-9-]+[.])+([a-zA-Z]{4}|net|NET|com|COM|gov|GOV|mil|MIL|org|ORG|edu|EDU|int|INT|name|shop|NAME|SHOP)\$";
#	var re = new RegExp(regu);
#	if (s.search(re) == -1)
#	{
#		window.alert ('ÇëÊäÈëÓĞĞ§ºÏ·¨µÄE-mailµØÖ·£¡')
#		return false;
#       }

$output .= qq~<tr><td bgcolor=$miscbacktwo><font color=$fontcolormisc><b>×¢²áÑéÖ¤Âë£º(ÑéÖ¤ÂëÓĞĞ§ÆÚÎª20·ÖÖÓ)</b><br>ÇëÊäÈëÓÒÁĞµÄÑéÖ¤Âë£¬ÊäÈë²»ÕıÈ·Ê±½«²»ÄÜÕı³£×¢²á¡£<br>£¨×¢Òâ£ºÖ»ÓĞÊı×Ö£¬ 0 ÊÇÁã¶ø²»ÊÇÓ¢ÎÄ×ÖÄ¸µÄ O£©</font></td><td bgcolor=$miscbacktwo><input type=hidden name=sessionid value="$sessionid"><input type=text name="verifynum" size=4 maxlength=4> * <img src=$imagesurl/verifynum/$sessionid.$houzhui align=absmiddle> Ò»¹²ÊÇËÄ¸öÊı×Ö£¬Èç¹û¿´²»Çå£¬ÇëË¢ĞÂ</td></tr>~  if ($useverify eq "yes");
$output .= qq~<tr><td bgcolor=$miscbackone><font color=$fontcolormisc><b>ÍÆ¼öÈËÓÃ»§Ãû£º</b><br>ÊÇË­ÍÆ¼öÄú¼ÓÈëÎÒÃÇµÄÉçÇøµÄ£¿(Õâ½«Ê¹ÄãµÄÍÆ¼öÈË»ı·ÖÖµÔö³¤)</td>
<td bgcolor=$miscbackone><input type=text name="recommender">&nbsp;ÈçÃ»ÓĞÇë±£³Ö¿Õ°×</td>
</tr></table></td></tr></table>
~;
    if ($advreg == 1) { 
	$advregister = "true"; 
	$advmode = qq~<td width=50%><INPUT id=advcheck name=advshow type=checkbox value=1 checked onclick=showadv()><span id="advance">¹Ø±Õ¸ü¶à×¢²áÑ¡Ïî</a></span> </td><td width=50%><input type=submit value="×¢ ²á" name=submit></td>~;
    } else {
	$advregister = "none"; 
	$advmode = qq~<td width=50%><INPUT id=advcheck name=advshow type=checkbox value=1 onclick=showadv()><span id="advance">ÏÔÊ¾¸ü¶à×¢²áÑ¡Ïî</a></span> </td><td width=50%><input type=submit value="×¢ ²á" name=submit></td>~;
    }
    $output .=qq~<table cellpadding=0 cellspacing=0 width=$tablewidth bgcolor=$tablebordercolor align=center id=adv style="DISPLAY: $advregister"><tr><td>
<table cellpadding=4 cellspacing=1 width=100%>
$qa
<tr><td bgcolor=$miscbacktwo valign=middle colspan=2 align=center> 
<font color=$fonthighlight><b>ÂÛÌ³ÃÜÂëÌáÊ¾ÎÊÌâºÍ´ğ°¸ÊÇ²»ÄÜ¹»ĞŞ¸ÄµÄ£¬Çë½÷É÷ÊäÈë£¡</b></font></td></tr>
<tr>
<td bgcolor=$miscbackone width=40%><font color=$fontcolormisc><b>ÏÔÊ¾ÓÊ¼şµØÖ·</b><br>ÄúÊÇ·ñÏ£ÍûÔÚÄú·¢±íÎÄÕÂÖ®ºóÏÔÊ¾ÄúµÄÓÊ¼ş£¿</td>
<td bgcolor=$miscbackone width=60%><font color=$fontcolormisc><input name="showemail" type="radio" value="yes" checked> ÊÇ¡¡ <input name="showemail" type="radio" value="msn"> MSN¡¡ <input name="showemail" type="radio" value="popo"> ÍøÒ×ÅİÅİ¡¡ <input name="showemail" type="radio" value="no"> ·ñ</font></td>
</tr><tr>
<td bgcolor=$miscbackone><font color=$fontcolormisc><b>ĞÔ±ğ</b></td><td bgcolor=$miscbackone>
<select name="sex" size="1">
<option value="no">±£ÃÜ </option>
<option value="m">Ë§¸ç </option>
<option value="f">ÃÀÅ® </option>
</select>
</td></tr>
<tr><td bgcolor=$miscbackone><font color=$fontcolormisc><b>×î¸ßÑ§Àú</b></td>
<td bgcolor=$miscbackone>
<select name="education" size="1">
<option value="±£ÃÜ">±£ÃÜ </option>
<option value="Ğ¡Ñ§">Ğ¡Ñ§ </option>
<option value="³õÖĞ">³õÖĞ </option>
<option value="¸ßÖĞ">¸ßÖĞ</option>
<option value="´ó×¨">´ó×¨</option>
<option value="±¾¿Æ">±¾¿Æ</option>
<option value="Ë¶Ê¿">Ë¶Ê¿</option>
<option value="²©Ê¿">²©Ê¿</option>
<option value="²©Ê¿ºó">²©Ê¿ºó</option>
</select>
</td></tr>
<tr><td bgcolor=$miscbackone><font color=$fontcolormisc><b>»éÒö×´¿ö</b></td>
<td bgcolor=$miscbackone>
<select name="marry" size="1">
<option value="±£ÃÜ">±£ÃÜ </option>
<option value="Î´»é">Î´»é </option>
<option value="ÒÑ»é">ÒÑ»é </option>
<option value="Àë»é">Àë»é </option>
<option value="É¥Å¼">É¥Å¼ </option>
</select>
</td></tr>
<td bgcolor=$miscbackone><font color=$fontcolormisc><b>Ö°Òµ×´¿ö</b></td>
<td bgcolor=$miscbackone>
<select name="work" size="1">
<option value="±£ÃÜ">±£ÃÜ </option>
<option value="¼ÆËã»úÒµ">¼ÆËã»úÒµ </option>
<option value="½ğÈÚÒµ">½ğÈÚÒµ </option>
<option value="ÉÌÒµ">ÉÌÒµ </option>
<option value="·şÎñĞĞÒµ">·şÎñĞĞÒµ </option>
<option value="½ÌÓıÒµ">½ÌÓıÒµ </option>
<option value="Ñ§Éú">Ñ§Éú </option>
<option value="¹¤³ÌÊ¦">¹¤³ÌÊ¦ </option>
<option value="Ö÷¹Ü£¬¾­Àí">Ö÷¹Ü£¬¾­Àí </option>
<option value="Õş¸®²¿ÃÅ">Õş¸®²¿ÃÅ </option>
<option value="ÖÆÔìÒµ">ÖÆÔìÒµ </option>
<option value="ÏúÊÛ/¹ã¸æ/ÊĞ³¡">ÏúÊÛ/¹ã¸æ/ÊĞ³¡ </option>
<option value="Ê§ÒµÖĞ">Ê§ÒµÖĞ </option>
</select>
</td></tr>
<tr><td bgcolor=$miscbackone><font color=$fontcolormisc><b>ÉúÈÕ£º</b>Èç²»ÏëÌîĞ´£¬ÇëÈ«²¿Áô¿Õ¡£´ËÏî¿ÉÑ¡</td>
<td bgcolor=$miscbackone><input type="text" name="year" size=4 maxlength=4>Äê 
  <select name="month">
      <option value="" selected></option>
      <option value="01">01</option>
      <option value="02">02</option>
      <option value="03">03</option>
      <option value="04">04</option>
      <option value="05">05</option>
      <option value="06">06</option>
      <option value="07">07</option>
      <option value="08">08</option>
      <option value="09">09</option>
      <option value="10">10</option>
      <option value="11">11</option>
      <option value="12">12</option>
  </select>ÔÂ
   <select name="day">
      <option value="" selected></option>
      <option value="01">01</option>
      <option value="02">02</option>
      <option value="03">03</option>
      <option value="04">04</option>
      <option value="05">05</option>
      <option value="06">06</option>
      <option value="07">07</option>
      <option value="08">08</option>
      <option value="09">09</option>
      <option value="10">10</option>
      <option value="11">11</option>
      <option value="12">12</option>
      <option value="13">13</option>
      <option value="14">14</option>
      <option value="15">15</option>
      <option value="16">16</option>
      <option value="17">17</option>
      <option value="18">18</option>
      <option value="19">19</option>
      <option value="20">20</option>
      <option value="21">21</option>
      <option value="22">22</option>
      <option value="23">23</option>
      <option value="24">24</option>
      <option value="25">25</option>
      <option value="26">26</option>
      <option value="27">27</option>
      <option value="28">28</option>
      <option value="29">29</option>
      <option value="30">30</option>
      <option value="31">31</option>
  </select>ÈÕ
</td>
</tr>
<tr><SCRIPT language=javascript>
function showsx(){document.images.usersxs.src="$imagesurl/sx/"+document.creator.usersx.options[document.creator.usersx.selectedIndex].value+".gif";}
</SCRIPT>
<td bgcolor=$miscbackone vAlign=top><font color=$fontcolormisc><b>ËùÊôÉúĞ¤£º</b><br>ÇëÑ¡ÔñÄãËùÊôµÄÉúĞ¤¡£</td>
<td bgcolor=$miscbackone><SELECT name=\"usersx\" onchange=showsx() size=\"1\"> <OPTION value=blank>±£ÃÜ</OPTION> <OPTION value=\"sx1\">×ÓÊó</OPTION> <OPTION value=\"sx2\">³óÅ£</OPTION> <OPTION value=\"sx3\">Òú»¢</OPTION> <OPTION value=\"sx4\">Ã®ÍÃ</OPTION> <OPTION value=\"sx5\">³½Áú</OPTION> <OPTION value=\"sx6\">ËÈÉß</OPTION> <OPTION value=\"sx7\">ÎçÂí</OPTION> <OPTION value=\"sx8\">Î´Ñò</OPTION> <OPTION value=\"sx9\">Éêºï</OPTION> <OPTION value=\"sx10\">ÓÏ¼¦</OPTION> <OPTION value=\"sx11\">Ğç¹·</OPTION> <OPTION value=\"sx12\">º¥Öí</OPTION></SELECT> <IMG border=0 name=usersxs src="$imagesurl/sx/blank.gif" align="absmiddle">
</TD></tr><tr>
<SCRIPT language=javascript>
function showxz(){document.images.userxzs.src="$imagesurl/star/"+document.creator.userxz.options[document.creator.userxz.selectedIndex].value+".gif";}
</SCRIPT>
<td bgcolor=$miscbackone vAlign=top><font color=$fontcolormisc><b>ËùÊôĞÇ×ù£º</b><br>ÇëÑ¡ÔñÄãËùÊôµÄĞÇ×ù¡£<br>Èç¹ûÄãÕıÈ·ÊäÈëÁËÉúÈÕµÄ»°£¬ÄÇÃ´´ËÏîÎŞĞ§£¡</td>
<td bgcolor=$miscbackone><SELECT name=\"userxz\" onchange=showxz() size=\"1\"> <OPTION value=blank>±£ÃÜ</OPTION> <OPTION value=\"z1\">°×Ñò×ù(3ÔÂ21--4ÔÂ19ÈÕ)</OPTION> <OPTION value=\"z2\">½ğÅ£×ù(4ÔÂ20--5ÔÂ20ÈÕ)</OPTION> <OPTION value=\"z3\">Ë«×Ó×ù(5ÔÂ21--6ÔÂ21ÈÕ)</OPTION> <OPTION value=\"z4\">¾ŞĞ·×ù(6ÔÂ22--7ÔÂ22ÈÕ)</OPTION> <OPTION value=\"z5\">Ê¨×Ó×ù(7ÔÂ23--8ÔÂ22ÈÕ)</OPTION> <OPTION value=\"z6\">´¦Å®×ù(8ÔÂ23--9ÔÂ22ÈÕ)</OPTION> <OPTION value=\"z7\">Ìì³Ó×ù(9ÔÂ23--10ÔÂ23ÈÕ)</OPTION> <OPTION value=\"z8\">ÌìĞ«×ù(10ÔÂ24--11ÔÂ21ÈÕ)</OPTION> <OPTION value=\"z9\">ÉäÊÖ×ù(11ÔÂ22--12ÔÂ21ÈÕ)</OPTION> <OPTION value=\"z10\">Ä§ôÉ×ù(12ÔÂ22--1ÔÂ19ÈÕ)</OPTION> <OPTION value=\"z11\">Ë®Æ¿×ù(1ÔÂ20--2ÔÂ18ÈÕ)</OPTION> <OPTION value=\"z12\">Ë«Óã×ù(2ÔÂ19--3ÔÂ20ÈÕ)</OPTION></SELECT> <IMG border=0 name=userxzs src="$imagesurl/star/blank.gif" width=15 height=15 align="absmiddle">
</TD>
</TR><tr>
<td bgcolor=$miscbackone><font color=$fontcolormisc><b>Ö÷Ò³µØÖ·£º</b><br>Èç¹ûÄúÓĞÖ÷Ò³£¬ÇëÊäÈëÖ÷Ò³µØÖ·¡£´ËÏî¿ÉÑ¡</td>
<td bgcolor=$miscbackone><input type=text name="homepage" value="http://"></td>
</tr><tr>
<td bgcolor=$miscbackone><font color=$fontcolormisc><b>OICQ ºÅ£º</b><br>Èç¹ûÄúÓĞ OICQ£¬ÇëÊäÈëºÅÂë¡£´ËÏî¿ÉÑ¡</td>
<td bgcolor=$miscbackone><input type=text name="oicqnumber"></td>
</tr><tr>
<td bgcolor=$miscbackone><font color=$fontcolormisc><b>ICQ ºÅ£º</b><br>Èç¹ûÄúÓĞ ICQ£¬ÇëÊäÈëºÅÂë¡£´ËÏî¿ÉÑ¡</td>
<td bgcolor=$miscbackone><input type=text name="icqnumber"></td>
</tr>$flaghtml<tr>
<script src=$imagesurl/images/comefrom.js></script>
<body onload="init()">
<td bgcolor=$miscbackone><font color=$fontcolormisc><b>À´×Ô£º</b><br>ÇëÊäÈëÄúËùÔÚ¹ú¼ÒµÄ¾ßÌåµØ·½¡£´ËÏî¿ÉÑ¡</td>
<td bgcolor=$miscbackone>
Ê¡·İ <select name="province" onChange = "select()"></select>¡¡³ÇÊĞ <select name="city" onChange = "select()"></select><br>
ÎÒÔÚ <input type=text name="newlocation" maxlength=12 size=12 style="font-weight: bold">¡¡²»ÄÜ³¬¹ı12¸ö×Ö·û£¨6¸öºº×Ö£©
</td>
</tr><tr>
<td bgcolor=$miscbackone><font color=$fontcolormisc><b>Ê±²î£º</b><br>
·şÎñÆ÷ËùÔÚÊ±Çø£º$basetimes<br>Èç¹ûÄúËùÔÚµÄÎ»ÖÃºÍ·şÎñÆ÷ÓĞÊ±²î£¬ÇëÊäÈë¡£<br>Äú¿´µ½ËùÓĞµÄÊ±¼ä½«°´ÕÕÄúËùÔÚµÄµØÇøÊ±¼äÏÔÊ¾¡£</td>
<td bgcolor=$miscbackone>
<select name="timedifference"><option value="-23">- 23</option><option value="-22">- 22</option><option value="-21">- 21</option><option value="-20">- 20</option><option value="-19">- 19</option><option value="-18">- 18</option><option value="-17">- 17</option><option value="-16">- 16</option><option value="-15">- 15</option><option value="-14">- 14</option><option value="-13">- 13</option><option value="-12">- 12</option><option value="-11">- 11</option><option value="-10">- 10</option><option value="-9">- 9</option><option value="-8">- 8</option><option value="-7">- 7</option><option value="-6">- 6</option><option value="-5">- 5</option><option value="-4">- 4</option><option value="-3">- 3</option><option value="-2">- 2</option><option value="-1">- 1</option><option value="0" selected>0</option><option value="1">+ 1</option><option value="2">+ 2</option><option value="3">+ 3</option><option value="4">+ 4</option><option value="5">+ 5</option><option value="6">+ 6</option><option value="7">+ 7</option><option value="8">+ 8</option><option value="9">+ 9</option><option value="10">+ 10</option><option value="11">+ 11</option><option value="12">+ 12</option><option value="13">+ 13</option><option value="14">+ 14</option><option value="15">+ 15</option><option value="16">+ 16</option><option value="17">+ 17</option><option value="18">+ 18</option><option value="19">+ 19</option><option value="20">+ 20</option><option value="21">+ 21</option><option value="22">+ 22</option><option value="23">+ 23</option></select> Ğ¡Ê±
</td>
</tr><tr>
<td bgcolor=$miscbackone><font color=$fontcolormisc><b>×ÔÎÒ¼ò½é£º </b><BR>²»ÄÜ³¬¹ı <B>$maxinsline</B> ĞĞ£¬Ò²²»ÄÜ³¬¹ı <B>$maxinslegth</B> ¸ö×Ö·û<br><br>Äú¿ÉÒÔÔÚ´ËÊäÈëÄúµÄ¸öÈË¼ò½é¡£´ËÏî¿ÉÑ¡</td>
<td bgcolor=$miscbackone><textarea name="interests" cols="60" rows="5"></textarea></td>
</tr><tr>
<td bgcolor=$miscbackone><font color=$fontcolormisc><b>Ç©Ãû£º</b><br>²»ÄÜ³¬¹ı <B>$maxsignline</B> ĞĞ£¬Ò²²»ÄÜ³¬¹ı <B>$maxsignlegth</B> ¸ö×Ö·û
<br><br>²»ÄÜÊ¹ÓÃ HTML ±êÇ©<br>¿ÉÒÔÊ¹ÓÃ <a href="javascript:openScript('misc.cgi?action=lbcode',300,350)">LeoBBS ±êÇ©</a><BR>
<li>ÌùÍ¼±êÇ©¡¡: <b>$signpicstates</b><li>Flash ±êÇ©: <b>$signflashstates</b><li>ÒôÀÖ±êÇ©¡¡: <b>$signsoundstates</b><li>ÎÄ×Ö´óĞ¡¡¡: <b>$signfontsizestates</b>
</td>
<td bgcolor=$miscbackone><textarea name="signature" cols="60" rows="8"></textarea></td>
</tr>
$avatarhtml
</table></td></tr><SCRIPT>valignend()</SCRIPT>
<script>
function showadv(){
if (document.creator.advshow.checked == true) {
adv.style.display = "";
advance.innerText="¹Ø±Õ¸ü¶àÓÃ»§ÉèÖÃÑ¡Ïî"
}else{
adv.style.display = "none";
advance.innerText="ÏÔÊ¾¸ü¶àÓÃ»§ÉèÖÃÑ¡Ïî"
}
}
</script>
</tr></table><img src="" width=0 height=4><BR>
<table cellpadding=0 cellspacing=0 width=$tablewidth align=center>
<tr>
$advmode 
<input type=hidden name=action value=addmember></form></tr></table><BR>
~;
}
else {
    require "cleanolddata.pl";
    &cleanolddata;
    $regdisptime = 15 if ($regdisptime <1);
    $filetoopen = "$lbdir" . "data/register.dat";
    open(FILE,$filetoopen);
    sysread(FILE, my $tempoutput,(stat(FILE))[7]);
    close(FILE);
    $tempoutput =~ s/\r//isg;

    $output .= qq~<tr>
    <td bgcolor=$titlecolor $catbackpic align=center>
    <form action="$thisprog" method="post" name="agree">
    <input name="action" type="hidden" value="agreed">
    <input type=hidden name="forum" value="$inforum">
    <font color=$fontcolormisc>
    <b>·şÎñÌõ¿îºÍÉùÃ÷</b>
    </td></tr>
    <td bgcolor=$miscbackone><font color=$fontcolormisc>
    $tempoutput
    </td></tr>
    <tr><td bgcolor=$miscbacktwo align=center>
    <center><input type="submit" value="ÇëÈÏÕæ²é¿´<·şÎñÌõ¿îºÍÉùÃ÷> ($regdisptime Ãëºó¼ÌĞø)" name="agreeb">¡¡¡¡
    <input onclick=history.back(-1) type="reset" value=" ÎÒ ²» Í¬ Òâ ">
    </center>
    </td></form></tr></table></td></tr></table><SCRIPT>valignend()</SCRIPT>
<SCRIPT language=javascript>
<!--
var secs = $regdisptime;
document.agree.agreeb.disabled=true;
for(i=1;i<=secs;i++) {
 window.setTimeout("update(" + i + ")", i * 1000);
}
function update(num) {
 if(num == secs) {
 document.agree.agreeb.value =" ÎÒ Í¬ Òâ ";
 document.agree.agreeb.disabled=false;
 }
else {
 printnr = secs-num;
 document.agree.agreeb.value = "ÇëÈÏÕæ²é¿´<·şÎñÌõ¿îºÍÉùÃ÷> (" + printnr +" Ãëºó¼ÌĞø)";
 }
}
//-->
</SCRIPT>

    ~;
}
print header(-cookie=>[$namecookie, $passcookie] , -expires=>"$EXP_MODE" , -cache=>"$CACHE_MODES");
&output("$boardname - ×¢²áĞÂÓÃ»§",\$output);
exit;

sub recommfunc {
    my $recommender = shift;
    $recommender =~ s/ /\_/g;
    $recommender =~ tr/A-Z/a-z/;
    $recommender =~ s/[\a\f\n\e\0\r\t\`\~\!\@\#\$\%\^\&\*\(\)\+\=\\\{\}\;\'\:\"\,\.\/\<\>\?]//isg;
    $namenumber = &getnamenumber($recommender);
    my $filetoopen = "${lbdir}$memdir/$namenumber/$recommender.cgi";
    if (-e $filetoopen) {
        &winlock($filetoopen) if ($OS_USED eq "Nt");
	open(REFILE,"+<$filetoopen");
	flock(REFILE, 2) if ($OS_USED eq "Unix");
	my $filedata = <REFILE>;
	chomp $filedata;
	($lmembername, $lpassword, $lmembertitle, $lmembercode, $lnumberofposts, $lemailaddress, $lshowemail, $lipaddress, $lhomepage, $loicqnumber, $licqnumber ,$llocation ,$linterests, $ljoineddate, $llastpostdate, $lsignature, $ltimedifference, $lprivateforums, $luseravatar, $luserflag, $luserxz, $lusersx, $lpersonalavatar, $lpersonalwidth, $lpersonalheight, $lrating, $llastgone, $lvisitno, $luseradd04, $luseradd02, $lmymoney, $lpostdel, $lsex, $leducation, $lmarry, $lwork, $lborn, $lchatlevel, $lchattime, $ljhmp, $ljhcount,$lebankdata,$lonlinetime,$luserquestion,$lawards,$ljifen,$luserface,$lsoccerdata,$luseradd5) = split(/\t/,$filedata);

		my ($numberofposts, $numberofreplys) = split(/\|/,$lnumberofposts);
		$numberofposts ||= "0";
		$numberofreplys ||= "0";
	      	$ljifen = $numberofposts * 2 + $numberofreplys - $lpostdel * 5 if ($ljifen eq "");

	$addtjjf = 0 if ($addtjjf eq "");
	$addtjhb = 0 if ($addtjhb eq "");
	if ($lmymoney eq "") { $lmymoney = $addtjhb; }
                   else { $lmymoney += $addtjhb; }

	$ljifen += $addtjjf;

	if (($lmembername ne "")&&($lpassword ne "")) {
	    seek(REFILE,0,0);
	    print REFILE "$lmembername\t$lpassword\t$lmembertitle\t$lmembercode\t$lnumberofposts\t$lemailaddress\t$lshowemail\t$lipaddress\t$lhomepage\t$loicqnumber\t$licqnumber\t$llocation\t$linterests\t$ljoineddate\t$llastpostdate\t$lsignature\t$ltimedifference\t$lprivateforums\t$luseravatar\t$luserflag\t$luserxz\t$lusersx\t$lpersonalavatar\t$lpersonalwidth\t$lpersonalheight\t$lrating\t$llastgone\t$lvisitno\t$luseradd04\t$luseradd02\t$lmymoney\t$lpostdel\t$lsex\t$leducation\t$lmarry\t$lwork\t$lborn\t$lchatlevel\t$lchattime\t$ljhmp\t$ljhcount\t$lebankdata\t$lonlinetime\t$luserquestion\t$lawards\t$ljifen\t$luserface\t$lsoccerdata\t$luseradd5\t";
	    close(REFILE);
   	} else {
	    close(REFILE);
	}
        &winunlock($filetoopen) if ($OS_USED eq "Nt");
    }
}

sub checkverify {
	my $verifynum = $query->param('verifynum');
	my $sessionid = $query->param('sessionid');
	$sessionid =~ s/[^0-9a-f]//isg;
	return 1 if (length($sessionid) != 32 && $useverify eq "yes");

	###»ñÈ¡ÕæÊµµÄ IP µØÖ·
	my $ipaddress = $ENV{'REMOTE_ADDR'};
	my $trueipaddress = $ENV{'HTTP_X_FORWARDED_FOR'};
	$ipaddress = $trueipaddress if (($trueipaddress ne "") && ($trueipaddress ne "unknown"));
	$trueipaddress = $ENV{'HTTP_CLIENT_IP'};
	$ipaddress = $trueipaddress if (($trueipaddress ne "") && ($trueipaddress ne "unknown"));

	###»ñÈ¡µ±Ç°½ø³ÌµÄÑéÖ¤ÂëºÍÑéÖ¤Âë²úÉúÊ±¼ä¡¢ÓÃ»§ÃÜÂë
	my $filetoopen = "${lbdir}verifynum/$sessionid.cgi";
	open(FILE, $filetoopen);
	my $content = <FILE>;
	close(FILE);
	chomp($content);
	my ($trueverifynum, $verifytime, $savedipaddress) = split(/\t/, $content);
	my $currenttime = time;
	return ($verifynum ne $trueverifynum || $currenttime > $verifytime + 1200 + 120 || $ipaddress ne $savedipaddress) ? 1 : 0;
}
