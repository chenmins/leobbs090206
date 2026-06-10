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
$LBCGI::POST_MAX=200000;
$LBCGI::DISABLE_UPLOADS = 1;
$LBCGI::HEADERS_ONCE = 1;
use VISITFORUM qw(getlastvisit setlastvisit);
require "code.cgi";
require "data/boardinfo.cgi";
require "data/cityinfo.cgi";
require "data/styles.cgi";
require "bbs.lib.pl";
$|++;
$thisprog = "printpage.cgi";
$query = new LBCGI;
eval ('$complevel = 9 if ($complevel eq ""); use WebGzip($complevel); $gzipused = 1;') if ($usegzip eq "yes");

&ipbanned; #封杀一些 ip

$inforum        = $query -> param('forum');
$intopic        = $query -> param('topic');

print header(-charset=>gb2312 , -expires=>"$EXP_MODE" , -cache=>"$CACHE_MODES");

&error("打开文件&老大，别乱黑我的程序呀！") if (($intopic) && ($intopic !~ /^[0-9]+$/));
&error("打开文件&老大，别乱黑我的程序呀！") if (($inforum) && ($inforum !~ /^[0-9]+$/));
if (-e "${lbdir}data/style${inforum}.cgi") { require "${lbdir}data/style${inforum}.cgi"; }

$inselectstyle   = $query->cookie("selectstyle");
$inselectstyle   = $skinselected if ($inselectstyle eq "");
&error("普通错误&老大，别乱黑我的程序呀！") if (($inselectstyle =~  m/\//)||($inselectstyle =~ m/\\/)||($inselectstyle =~ m/\.\./));
if (($inselectstyle ne "")&&(-e "${lbdir}data/skin/${inselectstyle}.cgi")) {require "${lbdir}data/skin/${inselectstyle}.cgi";}

if (! $inmembername) { $inmembername = $query->cookie("amembernamecookie"); }
if (! $inpassword) { $inpassword = $query->cookie("apasswordcookie"); }
$inmembername =~ s/[\a\f\n\e\0\r\t\`\~\!\@\#\$\%\^\&\*\(\)\+\=\\\{\}\;\'\:\"\,\.\/\<\>\?]//isg;
$inpassword =~ s/[\a\f\n\e\0\r\t\|\@\;\#\{\}\$]//isg;

if ($inmembername eq "" || $inmembername eq "客人" ) {
    $inmembername = "客人";
    $myrating = -1;
	    if ($regaccess eq "on" && &checksearchbot) {
	    	print header(-cookie=>[$namecookie, $passcookie] , -expires=>"$EXP_MODE" , -cache=>"$CACHE_MODES");
	    	print "<script language='javascript'>document.location = 'loginout.cgi?forum=$inforum'</script>";
	    	exit;
	    }
    &error("普通错误&客人不能查看贴子内容，请注册或登录后再试") if ($guestregistered eq "off");
}
else {
#    &getmember("$inmembername");
    &getmember("$inmembername","no");
    $mymembercode=$membercode;
    $myrating=$rating;
     if ($inpassword ne $password) {
	$namecookie        = cookie(-name => "amembernamecookie", -value => "", -path => "$cookiepath/");
	$passcookie        = cookie(-name => "apasswordcookie",   -value => "", -path => "$cookiepath/");
        print header(-cookie=>[$namecookie, $passcookie] , -expires=>"$EXP_MODE" , -cache=>"$CACHE_MODES");
        &error("普通错误&密码与用户名不相符，请重新登录！");
     }
    &error("普通错误&此用户根本不存在！") if ($userregistered eq "no");
#&getoneforum("$inforum");
#    &moderator("$inforum");
$myinmembmod = $inmembmod;
        &getlastvisit;
        $forumlastvisit = $lastvisitinfo{$inforum};
        $currenttime = time;
        &setlastvisit("$inforum,$currenttime");
    }
    &getoneforum("$inforum");
&doonoff;  #论坛开放与否

if ($privateforum eq "yes"){
    if ($inmembername eq "客人") {
	print "<script language='javascript'>document.location = 'loginout.cgi?forum=$inforum'</script>";
	exit;
    }
    if (($allowedentry{$inforum} eq "yes")||($membercode eq "ad")||($membercode eq 'smo')||($inmembmod eq "yes")) { $allowed = "yes"; } else { $allowed = "no"; }
}

&error("进入论坛&你的论坛组没有权限进入论坛！") if ($yxz ne '' && $yxz!~/,$membercode,/);
if ($allowusers ne ''){
    &error('进入论坛&你不允许进入该论坛！') if (",$allowusers," !~ /,$inmembername,/i && $membercode ne 'ad');
}

if ($membercode ne 'ad' && $membercode ne 'smo' && $inmembmod ne 'yes') {
    &error("进入论坛&你不允许进入该论坛，你的威望为 $rating，而本论坛只有威望大于等于 $enterminweiwang 的才能进入！") if ($enterminweiwang > 0 && $rating < $enterminweiwang);
    if ($enterminmony > 0 || $enterminjf > 0 ) {
	require "data/cityinfo.cgi" if ($addmoney eq "" || $replymoney eq "" || $moneyname eq "");
	$mymoney1 = $numberofposts * $addmoney + $numberofreplys * $replymoney + $visitno * $loginmoney + $mymoney - $postdel * $delmoney + $jhcount * $addjhhb;
	&error("进入论坛&你不允许进入该论坛，你的金钱为 $mymoney1，而本论坛只有金钱大于等于 $enterminmony 的才能进入！") if ($enterminmony > 0 && $mymoney1 < $enterminmony);
	&error("进入论坛&你不允许进入该论坛，你的积分为 $jifen，而本论坛只有积分大于等于 $enterminjf 的才能进入！") if ($enterminjf > 0 && $jifen < $enterminjf);
    }
}

    $filetoopen = "$lbdir" . "forum$inforum/$intopic.thd.cgi";
    &winlock($filetoopen) if ($OS_USED eq "Nt");
    open(FILE, "$filetoopen");
    flock(FILE, 1) if ($OS_USED eq "Unix");
    @threads = <FILE>;
    close(FILE);
    &winunlock($filetoopen) if ($OS_USED eq "Nt");

    
    ($no, $topictitle, $no, $no, $no ,$startedpostdate, $no) = split(/\t/, @threads[0]);
    $topictitle =~ s/^＊＃！＆＊//;

	if ($addtopictime eq "yes") {
	    my $topictime = &dispdate($startedpostdate + ($timedifferencevalue*3600) + ($timezone*3600));
	    $topictitle = "[$topictime] $topictitle";
	}

if (($startnewthreads eq "cert")&&(($membercode ne "ad" && $membercode ne "smo" && $membercode ne "cmo" && $membercode ne "mo" && $membercode ne "amo" && $membercode !~ /^rz/)||($inmembername eq "客人"))&&($userincert eq "no")) { &error("进入论坛&你一般会员不允许进入此论坛！"); }

    if (($privateforum eq "yes") && ($allowed ne "yes")) {
        &error("进入私密论坛&对不起，你无权访问这个论坛！");
    }
    else {
      my $filetoopens = "$lbdir" . "data/onlinedata.cgi";
      $filetoopens = &lockfilename($filetoopens);
      if (!(-e "$filetoopens.lck")) {
        if ($privateforum ne "yes") {
            &whosonline("$inmembername\t$forumname\tboth\t浏览<a href=\"topic.cgi?forum=$inforum&topic=$intopic\"><b>$topictitle</b></a>(文本方式)\t");
        }
        else {
            &whosonline("$inmembername\t$forumname(密)\tboth\t浏览保密贴子(文本方式)\t");
        }
      }
    }
if($category=~/childforum-[0-9]+/){
$tempforumno=$category;
$tempforumno=~s/childforum-//;
    $filetoopen = "${lbdir}forum$tempforumno/foruminfo.cgi";
    open(FILE, "$filetoopen");
    $forums = <FILE>;
    close(FILE);
    (undef, undef, undef, $tempforumname, undef) = split(/\t/,$forums);
    $addlink=qq~\n            <b>-- $tempforumname</b> ($boardurl/forums.cgi?forum=$tempforumno)<br>~;
    $addspace="-";
}

    $output .= qq~
    <html><head><title>$topictitle - $boardname</title>
	<style>
		A:visited {	TEXT-DECORATION: none	}
		A:active  {	TEXT-DECORATION: none	}
		A:hover   {	TEXT-DECORATION: underline overline	}
		A:link 	  {	text-decoration: none;}

	        A:visited {	text-decoration: none;}
	        A:active  {	TEXT-DECORATION: none;}
	        A:hover   {	TEXT-DECORATION: underline overline}

		.t     {	LINE-HEIGHT: 1.4			}
		BODY   {	FONT-FAMILY: 宋体; FONT-SIZE: 9pt	}
		TD	   {	FONT-FAMILY: 宋体; FONT-SIZE: 9pt	}
		SELECT {	FONT-FAMILY: 宋体; FONT-SIZE: 9pt;	}
		INPUT  {	FONT-FAMILY: 宋体; FONT-SIZE: 9pt; height:22px;	}
		TEXTAREA{	FONT-FAMILY: 宋体; FONT-SIZE: 9pt;	}
		DIV    {	FONT-FAMILY: 宋体; FONT-SIZE: 9pt	}
		FORM   {	FONT-FAMILY: 宋体; FONT-SIZE: 9pt	}
		OPTION {	FONT-FAMILY: 宋体; FONT-SIZE: 9pt	}
		P	   {	FONT-FAMILY: 宋体; FONT-SIZE: 9pt	}
		TD	   {	FONT-FAMILY: 宋体; FONT-SIZE: 9pt	}
		BR	   {	FONT-FAMILY: 宋体; FONT-SIZE: 9pt	}
	</style>
    </head>
    <body topmargin=10 leftmargin=0 onload="window.print()">
    <table cellpadding=0 cellspacing=0 width=90% align=center>
        <tr>
            <td>
            <p><b>以文本方式查看主题</b><p>
            <b>- $boardname</b> ($boardurl/leobbs.cgi)<br>$addlink
            <b>$addspace-- $forumname</b> ($boardurl/forums.cgi?forum=$inforum)<br>
            <b>$addspace--- $topictitle</b> ($boardurl/topic.cgi?forum=$inforum&topic=$intopic)
        </tr>
    </table>
    <p><p><p>
    <table cellpadding=0 cellspacing=0 width=90% align=center>
      <tr><td>
    ~;

if ($mymembercode eq "ad" or $mymembercode eq "smo" or $myinmembmod eq "yes") {
    $viewhide = 1;
}
else {
    $viewhide = 0;
    if ($hidejf eq "yes" ) { 
	my @viewhide=grep(/^$inmembername\t/i,@threads);
	$viewhide=@viewhide;
	$viewhide=1 if($viewhide >= 1);
    }
}
$StartCheck=$numberofposts+$numberofreplys;

$rn = 1;
    foreach $line (@threads) {
        ($membername, $topictitle, $postipaddress, $showemoticons, $showsignature, $postdate, $post) = split(/\t/,$line);
        if ($rn eq 1) {
            &getmember("$membername","no");
            if ($membercode eq "masked") {
    	        $addme = "";
                $post = qq(<br>------------------------<br><font color=$posternamecolor>此用户的发言已经被屏蔽！<br>如有疑问，请联系管理员！</font><br>------------------------<BR>);
            }
	}
#        $post = "(密)" if ($post=~/LBHIDDEN\[(.*?)\]LBHIDDEN/sg);
#        $post =~ s/(\[hide\])(.+?)(\[\/hide\])/(本部分内容已经隐藏)/isg;
#        $post =~s/\[post=(.+?)\](.+?)\[\/post\]/(本内容已被隐藏)/isg; 

    if ($wwjf ne "no") {
	if ($post=~/LBHIDDEN\[(.*?)\]LBHIDDEN/sg) {
    	    if ((lc($inmembername) eq lc($membername))||($mymembercode eq "ad") || ($mymembercode eq 'smo') || ($myinmembmod eq "yes")|| ($myrating >= $1) ){
	    }else{
		$post=qq~<FONT COLOR=$fonthighlight><B>[Hidden Post: Rating $1]</B></FONT> <BR>  <BR> <FONT COLOR=$posternamecolor>（您没有权限看这个帖子，您的威望至少需要 <B>$1<\/B>）</FONT><BR>  <BR> ~;
		$addme="附件保密!<br>";
	    }
	    $post=~s/LBHIDDEN\[(.*?)\]LBHIDDEN/<font color=$fonthighlight>（此贴只有威望大于等于 <B>$1<\/B> 的才能查看）<\/font><br>/sg;   
	}
    }
    else { $post=~s/LBHIDDEN\[(.*?)\]LBHIDDEN//; }

    $post  =~ s/\[ALIPAYE\](.*)\[ALIPAYE\]//isg; 

    if ($cansale ne "no") {
	if ($post=~/LBSALE\[(.*?)\]LBSALE/sg) {
    	    my $postno = $rn -1;
            my $isbuyer = "";
            my $allbuyer = "";
            my $allbuyerno = "";
            undef @allbuyer;
            if (open(FILE, "${lbdir}$saledir/$inforum\_$intopic\_$postno.cgi")) {
                my $allbuyer = <FILE>;
                close(FILE);
                chomp $allbuyer;
		$allbuyer =~ s/\t\t/\t/isg;
                $allbuyer =~ s/\t$//gi;
                $allbuyer =~ s/^\t//gi;
		@allbuyer = split(/\t/, $allbuyer);
		$allbuyerno = @allbuyer;
	        $allbuyer = "\t$allbuyer\t";
		$isbuyer="yes" if ($allbuyer =~ /\t$inmembername\t/i);
            }
            $allbuyerno = 0 if (($allbuyerno < 0)||($allbuyerno eq ""));
            unless ((lc($inmembername) eq lc($membername))||($mymembercode eq "ad")||($mymembercode eq 'smo')||($mymembercode eq 'mo')||($mymembercode eq 'amo')||($myinmembmod eq "yes")||($isbuyer eq "yes")) {
                $post=qq~<FONT COLOR=$fonthighlight><B>[Sale Post: Money $1]</B></FONT><BR>  <BR><FONT COLOR=$posternamecolor>[查看这个帖子需要 <b>$1</b> $moneyname，目前已有 <B>$allbuyerno</B> 人购买]</FONT><BR><br><FORM action=buypost.cgi method=post><input name=inforum type=hidden value=$inforum><input name=intopic type=hidden value=$intopic><input name=postnumber type=hidden value=$postno><input name=salemembername type=hidden value="$membername"><input name=moneynumber type=hidden value=$1><INPUT name=B1 type=submit value="算你狠。。我买，我付钱"></form><BR> ~;
                $addme="附件保密!<br>";
	    }
	    else {
	    	$buyeroutput = "";
	    	if ((lc($inmembername) eq lc($membername))||($mymembercode eq "ad")||($mymembercode eq 'smo')||($mymembercode eq 'mo')||($mymembercode eq 'amo')||($myinmembmod eq "yes")) {
                    if ($allbuyerno > 0 ) {
	                $buyeroutput = qq~<SCRIPT LANGUAGE="JavaScript">
function surfto(list) { var myindex1  = list.selectedIndex; if (myindex1 != 0 & myindex1 != 1) { var newwindow = list.options[myindex1].value; var msgwindow = window.open(newwindow,"",""); }}
</SCRIPT><form action="profile.cgi" method=post name="modjump"><img src=$imagesurl/images/team2.gif width=19 height=19 align=absmiddle>
<input type=hidden name=action value=show><select onchange="surfto(this)">
<option>购买名单：</option><option>------------</option>
~;
	                foreach (@allbuyer) {
	                    chomp $_;
	                    next if ($_ eq "");
	                    my $cleanedmodname = $_;
	                    $cleanedmodname =~ s/ /\_/g;
	                    $cleanedmodname =~ tr/A-Z/a-z/;
    	                    $buyeroutput .= qq~<option value="profile.cgi?action=show&member=$cleanedmodname">$_</option>~;
	                }
	                $buyeroutput .= qq~</select><BR>\n~;
                    }
                }
	        $post=~s/LBSALE\[(.*?)\]LBSALE/$buyeroutput<font color=$fonthighlight>（此贴售价 <B>$1<\/B> $moneyname，目前已有 <B>$allbuyerno<\/B> 人购买）<\/font><br><br>/sg;   
	    }
	}
    }
    else { $post=~s/LBSALE\[(.*?)\]LBSALE//; }

    if ($hidejf eq "yes" ) {
      if ($post =~m/(\[hide\])(.*)(\[\/hide\])/isg){ 
        if ($viewhide ne "1") { 
            $post =~ s/(\[hide\])(.*)(\[\/hide\])/<blockquote><font color=$posternamecolor>隐藏： <hr noshade size=1><font color=$fonthighlight>本部分内容已经隐藏，必须回复后，才能查看<\/font><hr noshade size=1><\/blockquote><\/font><\/blockquote>/isg;
            $addme="附件保密!<br><br>" if (($addme)&&($1 eq "[hide]"));
	} 
        else { 
            $post =~ s/\[hide\](.*)\[hide\](.*)\[\/quote](.*)\[\/hide\]/<blockquote><font color=$posternamecolor>隐藏： <hr noshade>$1<blockquote><hr noshade size=1>$2<hr noshade size=1><\/blockquote>$3<\/font><hr noshade><\/blockquote>/isg; 
     	    $post =~ s/\[hide\]\s*(.*?)\s*\[\/hide\]/<blockquote><font color=$posternamecolor>隐藏： <hr noshade size=1>$1<hr noshade size=1><\/blockquote><\/font>/isg; 
  	}
      }
    }

    if ($postjf eq "yes") {
	if ($post =~m/\[post=(\d+?)\](.+?)\[\/post\]/isg){ 
	    $viewusepost=$1; 
	    if ($StartCheck >= $viewusepost) { $Checkpost='ok'; } else { $Checkpost='not'; }

	    if(($Checkpost eq 'ok')||($mymembercode eq "ad")||($mymembercode eq "smo")||($myinmembmod eq "yes")||($membername eq $inmembername)){ 
	   	$post =~s/\[post=(\d+?)\](.+?)\[\/post\]/<blockquote><font color=$posternamecolor>文章内容：（发言总数须有 <B>$viewusepost<\/B> 才能查看本贴） <hr noshade size=1>$2<hr noshade size=1><\/font><\/blockquote>/isg; 
	    }else{ 
   		$post =~s/(\[post=(\d+?)\])(.*)(\[\/post\])/<blockquote><font color=$posternamecolor>文章内容： <hr noshade size=1><font color=$fonthighlight>本内容已被隐藏 , 发言总数须有 <B>$viewusepost<\/B> 才能查看<\/font><hr noshade size=1><\/font><\/blockquote>/isg; 
                $addme="附件保密!<br><br>" if (($addme)&&($1 =~ m/^\[post/));
   	    }
   	}
    }


    if ($jfmark eq "yes") {
	if ($post =~m/\[jf=(\d+?)\](.+?)\[\/jf\]/isg){ 
	    $jfpost=$1; 

	    if (($jfpost <= $jifen)||($mymembercode eq "ad")||($mymembercode eq "smo")||($myinmembmod eq "yes")||(lc($membername) eq lc($inmembername))){ 
	   	$post =~s/\[jf=(\d+?)\](.*)\[\/jf\]/<blockquote><font color=$posternamecolor>文章内容：（积分必须达到 <B>$jfpost<\/B> 才能查看本内容） <hr noshade size=1>$2<hr noshade size=1><\/font><\/blockquote>/isg; 
	    } else { 
	        &error("有问题&积分必须达到 $jfpost 才能查看，你目前的积分是 $jifen ！") if (($editpostnumber eq "1")&&($noviewjf eq "yes"));
   		$post =~s/(\[jf=(\d+?)\])(.*)(\[\/jf\])/<blockquote><font color=$posternamecolor>文章内容： <hr noshade size=1><font color=$fonthighlight>本内容已被隐藏 , 积分必须达到 <B>$jfpost<\/B> 才能查看<\/font><hr noshade size=1><\/font><\/blockquote>/isg;
                $addme="附件保密!<br><br>" if (($addme)&&($1 =~ m/^\[jf/));
   	    }
   	}
    }


#       	&lbcode(\$post);
	$post =~ s/\[USECHGFONTE\]//sg;
	$post =~ s/\[DISABLELBCODE\]//sg;
    $post =~ s/\[ADMINOPE=(.+?)\]//isg;

    if ($post =~ /\[POSTISDELETE=(.+?)\]/) {
    	if ($1 ne " ") { $presult = "<BR>屏蔽理由：$1<BR>"; } else { $presult = "<BR>"; }
        $post = qq(<br>--------------------------<br><font color=$posternamecolor>此帖子内容已经被单独屏蔽！$presult如有疑问，请联系管理员！</font><br>--------------------------<BR>);
    }

        $postdate = &dateformat($postdate + ($timedifferencevalue*3600) + ($timezone*3600));
$post =~ s/\[watermark\](.+?)\[\/watermark\]/<font color=red>加水印内容不能打印<\/font>/isg;
$post =~ s/\[curl=\s*(http|https|ftp):\/\/(.*?)\s*\]/\[加密连结\]/isg if ($usecurl ne "no");

        $output .= qq~
        <p>
        <hr><p>
        -- 作者： $membername<BR>
        -- 发布时间： $postdate<p>
        $post
        <p><p>
        ~;
        $rn ++;
    }
    my $boardcopyright = qq(&copy\; $copyrightinfo) if $copyrightinfo;

   $boardcopyright =~ s/&lt;/</g; $boardcopyright =~ s/&gt;/>/g; $boardcopyright =~ s/&quot;/\"/g;

    $output .= qq~
        </td></tr></table><center><hr width=90%><font color=$fontcolormisc>
           $boardcopyright　 版本： $versionnumber
           </font></center>
        </body></html>
    ~;
    print $output;
    exit;
