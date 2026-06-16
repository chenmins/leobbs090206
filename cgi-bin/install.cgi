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
$LBCGI::POST_MAX = 200000;
$LBCGI::DISABLE_UPLOADS = 1;
$LBCGI::HEADERS_ONCE = 1;

$versionnumber = "LeoBBS X Build060331";

$|++;
$query = new LBCGI;
$action = $query->param('action');

$mypath = mypath(); #    	·µ»Øµ±Ç°µÄ¾ø¶ÔÂ·¾¶ (ÕıÈ·) ×îºóÃ»ÓĞ /
$myurl  = myurl();  #    	·µ»Øµ±Ç°µÄ URL Â·¾¶ (ÕıÈ·) ×îºóÃ»ÓĞ /
($html_dir, $html_url) = split(/\|/,myimgdir()); # ·µ»Øµ±Ç°Í¼ÏñÄ¿Â¼µÄ¾ø¶ÔÂ·¾¶ºÍ url Â·¾¶ (²»Ò»¶¨ÕıÈ·) ×îºóÃ»ÓĞ /

if (-e "$mypath/data/install.lock") {
    &output("<BR><BR><BR><font size=+1 color=red><center>¾¯¸æ£¡£¡°²×°³ÌĞò±»Ëø¶¨£¬ÎŞ·¨ÖØ¸´°²×°¡£<BR><BR><BR>ÇëÊÖ¹¤É¾³ı data Ä¿Â¼ÏÂµÄ install.lock ÎÄ¼şºóÖØĞÂÔËĞĞ¡£</center></font><BR><BR><BR>");
    exit;
}

if ($action eq "") {
    $output = qq~
<script>
function selectimg(){
document.bbsimg.src = FORM.imagesurl.value+"/images/teamad.gif";}
</script>
<BR>
¡¡¡¡ÔÚ½øĞĞ°²×°Ç°£¬ÇëÏÈÈ·¶¨ÄúÒÑ¾­ÍêÕûÉÏ´«ÁËÕû¸öÂÛÌ³³ÌĞòºÍÍ¼Æ¬ÎÄ¼ş£¬²¢ÒÑ¾­°´ÕÕÒªÇóÉèÖÃºÃÁËËùÓĞÄ¿Â¼ºÍÎÄ¼şµÄÊôĞÔ¡£<BR>
¡¡¡¡ÏÂÃæ 1 ºÍ 2 ÖĞµÄÄ¬ÈÏÉèÖÃÊÇÓÉ³ÌĞò×Ô¶¯ÅĞ¶ÏÉú³ÉµÄ£¬ÊÊÓÃÓÚ´ó²¿·Ö°²×°±¾³ÌĞòµÄ¿Í»§£¬Èç¹ûÓĞ´íÎó£¬Çë×ÔĞĞĞŞ¸Ä³ÉÕıÈ·µÄÖµ¡£<BR><BR>
¡¡¡¡¡î <a href=http://www.leobbs.com/leobbs/buy.asp target=_blank><B>Èç¹ûÒòÎªÄúË®Æ½ÓĞÏŞ¶øÎŞ·¨Õı³£°²×°ºÍÊ¹ÓÃ±¾ÂÛÌ³£¬Çë°´´Ë×¢²á±¾ÂÛÌ³ÉÌÒµ°æ£¬»ñµÃ°²×°Ê¹ÓÃĞ­ÖúµÈ¼¼ÊõÖ§³ÖÓë·şÎñ¡£</B></a><BR><BR>
<form action="install.cgi" method=POST name=FORM>
<input name=action type=hidden value="proceed">
¡¡<font color=red><B>1.</B> </font><font color=blue>ÉèÖÃ³ÌĞò½Å±¾µÄÂ·¾¶£¨Ò»°ãÇé¿öÏÂ£¬×Ô¶¯ÅĞ¶Ï³ÌĞò»ñµÃÕâÀïµÄÊı¾İ¶¼ÊÇÕıÈ·µÄ£©</font><BR>
¡¡½Å±¾³ÌĞò(cgi-bin)µÄ°²×°Â·¾¶¡¡¡¡<input name=lbdir type=text size=55 value="$mypath/">¡¡<font color=red>½áÎ²ÓĞ "/"</font><br>
¡¡½Å±¾³ÌĞò(cgi-bin)µÄ URL Â·¾¶¡¡ <input name=boardurl type=text size=55 value="$myurl">¡¡<font color=red>½áÎ²Ã»ÓĞ "/"</font><br>
<br><br>
¡¡<font color=red><B>2.</B> </font><font color=blue>ÉèÖÃÍ¼ÏñÎÄ¼şµÄÂ·¾¶£¨Èç¹ûµÚ¶şĞĞµÄ×îºóÓĞĞ¦Á³Í¼µÄ»°£¬¾ÍËµÃ÷µÚ¶şĞĞÌîĞ´µÄÊı¾İÊÇÕıÈ·µÄ£¬·ñÔòÇë×ÔĞĞĞŞ¸ÄÌîĞ´£©</font><BR>
¡¡Í¼ÏñÎÄ¼ş(non-cgi)µÄ°²×°Â·¾¶¡¡¡¡<input name=imagesdir type=text size=55 value="$html_dir/">¡¡¡¡¡¡<font color=red>½áÎ²ÓĞ "/"</font><br>
¡¡Í¼ÏñÎÄ¼ş(non-cgi) URL Â·¾¶¡¡ ¡¡<input name=imagesurl type=text size=55 value="$html_url" onChange=selectimg() onkeydown=selectimg() onkeyup=selectimg() onselect=selectimg()> <img name=bbsimg src=$html_url/images/teamad.gif width=16 height=14 title=Èç¹ûÄãÄÜ¿´µ½ÕâÕÅĞ¦Á³Í¼µÄ»°£¬¾ÍËµÃ÷ÕâÀïÌîĞ´µÄÊı¾İÊÇÕıÈ·µÄ>¡¡<font color=red>½áÎ²Ã»ÓĞ "/"</font><br>
<br><br><br>
¡¡<font color=red><B>3.</B> </font><font color=blue>ÉèÖÃ³õÊ¼»¯¹ÜÀíÔ±£¨Èç¹ûÊÇÉı¼¶°²×°µÄ»°£¬ÄÇÃ´ÕâÀïÊÇÎŞĞèÌîĞ´µÄ£¬ÇëÎñ±ØÁô¿Õ£©</font><BR>
¡¡³õÊ¼¹ÜÀíÔ±ÓÃ»§Ãû¡¡¡¡<input name=adminname type=text size=14 maxlenght=12>¡¡¡¡¡¡¡¡¿ªÍ·²»ÒªÊ¹ÓÃ¿ÍÈË×ÖÑù£¬Ò²²»Òª³¬¹ı12¸ö×Ö·û£¨6¸öºº×Ö£©<br>
¡¡³õÊ¼¹ÜÀíÔ±ÃÜÂë¡¡¡¡¡¡<input name=adminpass type=password size=20>¡¡Ö»ÔÊĞí´óĞ¡Ğ´×ÖÄ¸ºÍÊı×ÖµÄ×éºÏ£¬²»ÄÜÈ«²¿ÊÇÊı×Ö£¬²¢²»µÃÉÙÓÚ8¸ö×Ö·û<br>
¡¡³õÊ¼¹ÜÀíÔ±ÃÜÂë¡¡¡¡¡¡<input name=adminpass1 type=password size=20>¡¡Çë°´ÕÕÉÏÒ»ĞĞÔÙÖØĞÂÊäÒ»±é£¬ÒÔ±ãÈ·¶¨£¡<br>
<br><BR>
<center><input type=submit value=" Éè ¶¨ Íê ±Ï " OnClick="return confirm('È·¶¨ÉèÖÃÕıÈ·²¢±£´æÃ´£¿');"></form>
~;
   &output("$output");
   exit;
}

if ($action eq "proceed") {
	$lbdir     = $query->param("lbdir");
	$lbdir     =~ s/\/$//isg;
	$mypath    = $lbdir;
	$lbdir     = "${lbdir}/";
	$boardurl  = $query->param("boardurl");
	$boardurl  =~ s/\/$//isg;
	$imagesdir = $query->param("imagesdir");
	$imagesdir =~ s/\/$//isg;
	$imagesdir = "${imagesdir}/";
	$imagesurl = $query->param("imagesurl");
	$imagesurl =~ s/\/$//isg;
	$adminname = $query->param("adminname");
	$adminpass = $query->param("adminpass");
	$adminpass1= $query->param("adminpass1");

	unlink ("$mypath/record.cgi");
	opendir (DIRS, "$mypath");
	my @files = readdir(DIRS);
	closedir (DIRS);
	my @searchdir = grep(/^search/i, @files);
	$searchdir = @searchdir;
	my @memdir = grep(/^members/i, @files);
	$memdir = @memdir;
	my @msgdir = grep(/^messages/i, @files);
	$msgdir = @msgdir;
	my @recorddir = grep(/^record/i, @files);
	$recorddir = @recorddir;
	my @ftpdir = grep(/^ftpdata/i, @files);
	$ftpdir = @ftpdir;
	my @memfavdir = grep(/^memfav/i, @files);
	$memfavdir = @memfavdir;

	if (($searchdir > 2)||($memdir > 1)||($msgdir > 1)||($recorddir > 1)||($ftpdir > 1)||($memfavdir > 1)) {
	    if ($searchdir > 2)    { $output = "search ¿ªÍ·µÄÄ¿Â¼ÓĞÁ½¸ö»òÁ½¸öÒÔÉÏ"; }
	    elsif ($memdir > 1)    { $output = "members ¿ªÍ·µÄÄ¿Â¼ÓĞÁ½¸ö»òÁ½¸öÒÔÉÏ"; }
	    elsif ($recorddir > 1) { $output = "record ¿ªÍ·µÄÄ¿Â¼ÓĞÁ½¸ö»òÁ½¸öÒÔÉÏ"; }
	    elsif ($ftpdir > 1)    { $output = "ftpdata ¿ªÍ·µÄÄ¿Â¼ÓĞÁ½¸ö»òÁ½¸öÒÔÉÏ"; }
	    elsif ($msgdir > 1)    { $output = "messages ¿ªÍ·µÄÄ¿Â¼ÓĞÁ½¸ö»òÁ½¸öÒÔÉÏ"; }
	    elsif ($memfavdir > 1) { $output = "memfav ¿ªÍ·µÄÄ¿Â¼ÓĞÁ½¸ö»òÁ½¸öÒÔÉÏ"; }
	    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>$mypath Ä¿Â¼ÏÂµÄÒÔ $output£¬<BR><BR>ÇëÉ¾³ı¶àÓàµÄ£¬±£³Ö´ËÏà¹ØÄ¿Â¼Ö»ÓĞÒ»¸ö£¬È»ºóÖØĞÂÔËĞĞ°²×°³ÌĞòÒ»´Î¡£</font><BR><BR><BR>");
	    exit;
	}

	$memdir = $memdir[0];
	$msgdir = $msgdir[0];
	$memfavdir = $memfavdir[0];
	&changemod($mypath, $html_dir);
	chmod(0777,"$mypath/$memdir");
	mkdir("$mypath/$memdir/old",0777) unless (-e "$mypath/$memdir/old");
	chmod(0777,"$mypath/$memdir/old");
	chmod(0777,"$mypath/data");
	$memdirwritabler = $memdirwritabler1 = $datadirwritabler ="";
	$makefile = "$mypath/$memdir/test.txt";
	open (TEST, ">$makefile") or $memdirwritabler = "Ä¿Â¼ $mypath/$memdir Îª²»¿ÉĞ´£¬Çë¸Ä±äÊôĞÔÎª 777 ¡£<BR>";
	print TEST "-";
	close (TEST);
	$memdirwritabler = "Ä¿Â¼ $mypath/$memdir Îª²»¿ÉĞ´£¬Çë¸Ä±äÊôĞÔÎª 777 ¡£<BR>" if (!(-e "$makefile"));
	unlink "$makefile";
	$makefile = "$mypath/$memdir/old/test.txt";
	open (TEST, ">$makefile") or $memdirwritabler1 = "Ä¿Â¼ $mypath/$memdir/old Îª²»¿ÉĞ´£¬Çë¸Ä±äÊôĞÔÎª 777 ¡£<BR>";
	print TEST "-";
	close (TEST);
	$memdirwritabler1 = "Ä¿Â¼ $mypath/$memdir/old Îª²»¿ÉĞ´£¬Çë¸Ä±äÊôĞÔÎª 777 ¡£<BR>" if (!(-e "$makefile"));
	unlink "$makefile";
	$makefile = "$mypath/data/test.txt";
	open (TEST, ">$makefile") or $datadirwritabler = "Ä¿Â¼ $mypath/data Îª²»¿ÉĞ´£¬Çë¸Ä±äÊôĞÔÎª 777 ¡£<BR>";
	print TEST "-";
	close (TEST);
	$datadirwritabler = "Ä¿Â¼ $mypath/data Îª²»¿ÉĞ´£¬Çë¸Ä±äÊôĞÔÎª 777 ¡£<BR>" if (!(-e "$makefile"));
	unlink "$makefile";
	if (($memdirwritabler ne "")||($memdirwritabler1 ne "")||($datadirwritabler)) {
	    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>$datadirwritabler$memdirwritabler$memdirwritabler1</font><BR><BR><BR>");
	    exit;
	}

	chmod(0666,"${lbdir}data/boardinfo.cgi");

	if (!(-e "${lbdir}data/boardinfo.cgi")) {
	    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>Î´·¢ÏÖ ${lbdir}data/boardinfo.cgi ÎÄ¼ş£¬¿ÉÄÜÄúÊäÈëµÄ *.cgi ½Å±¾µÄ°²×°Â·¾¶´íÎó£¬Çë·µ»ØÖØĞÂÊäÈë¡£</font><BR><BR><BR>");
   	    exit;
	}
	if (!(-e "${imagesdir}images/logo.gif")) {
	    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>Î´·¢ÏÖ ${imagesdir}images/logo.gif ÎÄ¼ş£¬¿ÉÄÜÄúÊäÈëµÄ image Í¼ÏñÎÄ¼şµÄ°²×°Â·¾¶´íÎó£¬Çë·µ»ØÖØĞÂÊäÈë¡£</font><BR><BR><BR>");
   	    exit;
	}

	if (($adminname ne "")&&($adminpass ne "")) {
		$adminnametemp = $adminname;
		$adminname =~ s/\&nbsp\;//ig;
		$adminname =~ s/¡¡/ /g;
		$adminname =~ s/©¡/ /g;
		$adminname =~ s/[ ]+/ /g;
		$adminname =~ s/[ ]+/_/;
		$adminname =~ s/[_]+/_/;
		$adminname =~ s/ÿ//isg;
		$adminname =~ s///isg;
		$adminname =~ s/¡¡//isg;
		$adminname =~ s/©¡//isg;
		$adminname =~ s/()+//isg;
		$adminname =~ s/[\a\f\n\e\0\r\t\`\~\!\@\#\$\%\^\&\*\(\)\+\=\\\{\}\;\'\:\"\,\.\/\<\>\?\[\]]//isg;
		$adminname =~ s/\s*$//g;
		$adminname =~ s/^\s*//g;
		if ($adminnametemp ne $adminname) {
		    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>ÄúÊäÈëµÄ¹ÜÀíÔ±ÓÃ»§ÃûÓĞÎÊÌâ£¬Çë·µ»ØÖØĞÂÊäÈë£¡</font><BR><BR><BR>");
   		    exit;
		}
		if ($adminname =~ /^¿ÍÈË/) {
		    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>Çë²»ÒªÔÚ¹ÜÀíÔ±ÓÃ»§ÃûµÄ¿ªÍ·ÖĞÊ¹ÓÃ¿ÍÈË×ÖÑù£¬Çë·µ»ØÖØĞÂÊäÈë£¡</font><BR><BR><BR>");
   		    exit;
		}
    		if (length($adminname)>12) {
		    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>¹ÜÀíÔ±ÓÃ»§ÃûÌ«³¤£¬Çë²»Òª³¬¹ı12¸ö×Ö·û£¨6¸öºº×Ö£©£¬Çë·µ»ØÖØĞÂÊäÈë£¡</font><BR><BR><BR>");
   		    exit;
    		}
    		if (length($adminname)<2)  {
		    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>¹ÜÀíÔ±ÓÃ»§ÃûÌ«¶ÌÁË£¬Çë²»ÒªÉÙì¶2¸ö×Ö·û£¨1¸öºº×Ö£©£¬Çë·µ»ØÖØĞÂÊäÈë£¡</font><BR><BR><BR>");
   		    exit;
    		}

	        if ($adminpass =~ /[^a-zA-Z0-9]/) {
		    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>¹ÜÀíÔ±ÃÜÂëÖ»ÔÊĞí´óĞ¡Ğ´×ÖÄ¸ºÍÊı×ÖµÄ×éºÏ£¬Çë·µ»Øºó¸ü»»£¡</font><BR><BR><BR>");
   		    exit;
	        }
		if ($adminpass =~ /^lEO/) {
		    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>¹ÜÀíÔ±ÃÜÂë²»ÔÊĞíÊÇ lEO ¿ªÍ·£¬Çë·µ»Øºó¸ü»»£¡</font><BR><BR><BR>");
   		    exit;
		}
	        if (length($adminpass)<8) {
		    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>¹ÜÀíÔ±ÃÜÂëÌ«¶ÌÁË£¬Çë·µ»Øºó¸ü»»£¨ÃÜÂë±ØĞë 8 Î»ÒÔÉÏ£©£¡</font><BR><BR><BR>");
   		    exit;
	        }
		if ($adminpass =~ /^[0-9]+$/) {
		    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>¹ÜÀíÔ±ÃÜÂë²»ÄÜÈ«²¿ÎªÊı×Ö£¬Çë·µ»Øºó¸ü»»£¡</font><BR><BR><BR>");
   		    exit;
		}
		if ($adminname eq $adminpass) {
		    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>²»Òª½«¹ÜÀíÔ±ÓÃ»§ÃûºÍ¹ÜÀíÔ±ÃÜÂëÉèÖÃ³ÉÏàÍ¬µÄ£¬Çë·µ»Øºó¸ü»»£¡</font><BR><BR><BR>");
   		    exit;
		}
		if ($adminpass ne $adminpass1) {
		    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>¶Ô²»Æğ£¬ÄúÊäÈëµÄÁ½´Î¹ÜÀíÔ±ÃÜÂë²»ÏàÍ¬£¬Çë·µ»ØÖØĞÂÊäÈë£¡</font><BR><BR><BR>");
   		    exit;
		}
	}
	
	open(FILE, "${lbdir}data/boardinfo.cgi");
	@info = <FILE>;
	close(FILE);

	if (open(FILE, ">${lbdir}data/boardinfo.cgi")) {
	    print FILE "\$lbdir = '$lbdir';\n";
	    print FILE "\$boardurl = '$boardurl';\n";
	    print FILE "\$imagesdir = '$imagesdir';\n";
	    print FILE "\$imagesurl = '$imagesurl';\n";

	    eval('flock(FILE, 2);');
	    print FILE $@ ne '' ? "\$OS_USED = 'Nt';\n" : "\$OS_USED = 'Unix';\n";

	    foreach (@info) {
		chomp;
		next if (($_ =~ /^\$lbdir/)||($_ =~ /^\$imagesdir/)||($_ =~ /^\$boardurl/)||($_ =~ /^\$imagesurl/)||($_ =~ /^\$OS_USED/)||($_ eq ""));
		print FILE "$_\n";
	    }
	    print FILE "\n";
	    close(FILE);
	} else {
	    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>${lbdir}data/boardinfo.cgi ÎÄ¼ş²»¿ÉĞ´£¬ÇëÊÖ¹¤ÉèÖÃÆäÊôĞÔÎª 666 £¬È»ºóË¢ĞÂ±¾Ò³Ãæ¼ÌĞø¡£</font><BR><BR><BR>");
   	    exit;
	}

	if (($adminname ne "")&&($adminpass ne "")) {
		$oldadminname = $adminname;
		$adminname =~ s/ /\_/g;
		$adminname =~ tr/A-Z/a-z/;
	        my $namenumber = ((ord(substr($adminname,0,1))&0x3c)<<3)|((ord(substr($adminname,1,1))&0x7c)>>2);
#		my $namenumber = int((ord(substr($adminname,0,1))+ord(substr($adminname,1,1)))/2);
		mkdir ("${lbdir}$memdir/$namenumber", 0777) if (!(-e "${lbdir}$memdir/$namenumber"));
		chmod(0777,"${lbdir}$memdir/$namenumber");
		if ((-e "$lbdir$memdir/$namenumber/$adminname.cgi")||(-e "$lbdir$memdir/old/$adminname.cgi")) {
		    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>¹ÜÀíÔ±ÕËºÅ $oldadminname ÒÑ¾­´æÔÚ£¬Çë·µ»Ø¸ü»»£¡</font><BR><BR><BR>");
   		    exit;
		}
	        eval {$adminpass = md5_hex($adminpass);};
	        if ($@) {eval('use Digest::MD5 qw(md5_hex);$adminpass = md5_hex($adminpass);');}
	        unless ($@) {$adminpass = "lEO$adminpass";}

		opendir(DIR, $lbdir);
		@files = readdir(DIR);
		closedir(DIR);
		@memdirs = grep(/^members/i, @files);
		$memdir = $memdirs[0];
		chmod(0777,"$lbdir$memdir");
		mkdir("$lbdir$memdir/old",0777) unless (-e "$lbdir$memdir/old");
		chmod(0777,"$lbdir$memdir/old");
		my $currenttime = time;
		
		if (open(FILE, ">$lbdir$memdir/$namenumber/$adminname.cgi")) {
		    print FILE "$adminname\t$adminpass\tmember\tad\t0|0\t\tno\t±£ÃÜ\t\t\t\t\t\t$currenttime\t\t";
		    close(FILE);
		} else {
		    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>${lbdir}$memdir Ä¿Â¼²»¿ÉĞ´£¬ÇëÊÖ¹¤ÉèÖÃÆäÊôĞÔÎª 777 £¬È»ºóË¢ĞÂ±¾Ò³Ãæ¼ÌĞø¡£</font><BR><BR><BR>");
   		    exit;
		}
		if (open(FILE, ">$lbdir$memdir/old/$adminname.cgi")) {
		    print FILE "$adminname\t$adminpass\tmember\tad\t0|0\t\tno\t±£ÃÜ\t\t\t\t\t\t$currenttime\t\t";
		    close(FILE);
		} else {
		    unlink("$lbdir$memdir/$namenumber/$adminname.cgi");
		    &output("<BR><font size=+1 color=red><center>°²×°³ÌĞò·¢ÏÖ´íÎó£¡</font><BR><BR><BR>${lbdir}$memdir/old Ä¿Â¼²»¿ÉĞ´£¬ÇëÊÖ¹¤ÉèÖÃÆäÊôĞÔÎª 777 £¬È»ºóË¢ĞÂ±¾Ò³Ãæ¼ÌĞø¡£</font><BR><BR><BR>");
   		    exit;
		}
		$output = "¹ÜÀíÔ±ÕËºÅ $oldadminname¡¡½¨Á¢³É¹¦£¡";
	}

	open(LOCK, ">${lbdir}data/install.lock");
	print LOCK "www.LeoBBS.com";
	close(LOCK);
	unlink("${lbdir}install.cgi") if (!(-e "${lbdir}data/install.lock"));
	&changedirname();  # ¸ü¸ÄÓÃ»§¹Ø¼üÄ¿Â¼µÄÃû³Æ
        &output("<BR><font size=+1 color=red><center>ÂÛÌ³°²×°Íê³É£¡$output</font><BR><BR><BR>ÂÛÌ³°²×°ÒÑ¾­Ë³ÀûÍê³É£¡Ä¿Ç°°²×°³ÌĞòÒÑ¾­×Ô¶¯Ëø¶¨£¬ÎŞ·¨ÔÙ´ÎÖ´ĞĞ£¬µ«ÎÒÃÇ»¹ÊÇÇ¿ÁÒ½¨ÒéÄúÖ±½Ó½«Æä´Ó·şÎñÆ÷ÉÏÉ¾³ı¡£<BR><BR>Èç¹ûĞèÒªÔÙ´ÎÔËĞĞ°²×°³ÌĞò£¬ÇëÏÈÊÖ¹¤½« data Ä¿Â¼ÏÂµÄ install.lock ÎÄ¼şÉ¾³ı£¬È»ºóÔÙÔËĞĞ°²×°³ÌĞò£¡<BR><BR><BR>ÏÖÔÚÄú¿ÉÒÔÊ¹ÓÃ¹ÜÀíÔ±ÕËºÅºÍÃÜÂë½øÈë <a href=admin.cgi><B>ÂÛÌ³¹ÜÀíÖĞĞÄ</B></a> ÖØĞÂÉèÖÃËùÓĞ»ù±¾±äÁ¿ºÍ·ç¸ñ²ÎÊı¡£<BR><BR><BR>");
        $versionnumber =~ s/\<(.+?)\>//isg;
	&sendurlinfo("www.leobbs.com","download/reg.cgi","ver=$versionnumber&url=$boardurl") if (($boardurl ne "")&&($boardurl !~ m/localhost/i)&&($boardurl !~ m/127\.0\.0\./i)&&($boardurl !~ m/192\.168\./i));
        exit;
}

# ²ÎÊı²»¶Ô£®
&output("<BR><BR><BR><font size=+1 color=red><center>Çë²»ÒªºúÂÒÔËĞĞ±¾³ÌĞò£¬Ğ»Ğ»ºÏ×÷£¡</center></font><BR><BR><BR>");
exit;

sub output {
    my $outputinfo = shift;
    print header(-charset=>gb2312 , -expires=>"$EXP_MODE" , -cache=>"$CACHE_MODES");
    print qq~
<html>
  <head>
    <title>LeoBBS X °²×°³ÌĞò</title>
    <style type="text/css">
    A:visited{TEXT-DECORATION: none}
    A:active{TEXT-DECORATION: none}
    A:hover{TEXT-DECORATION: underline overline}
    A:link{text-decoration: none;}
    .h        { font-family: ËÎÌå; font-size: 12px; color: #FF0000 }
    .t        { font-family: ËÎÌå; font-size: 11px; color: #000003 }
    .ti       { font-family: ËÎÌå; font-size: 12px; color: #000003; font-weight: bold }
    .l        { font-family: ËÎÌå; font-size: 14px; font-weight: bold; color: #FFFFFF }
    BODY{FONT-FAMILY: ËÎÌå; FONT-SIZE: 9pt;}
    caption,TD,DIV,form ,OPTION,P,TD,BR{FONT-FAMILY: ËÎÌå; FONT-SIZE: 9pt} 
    INPUT, SUBMIT { font-family: ËÎÌå; font-size: 9pt; font-family: ËÎÌå; vertical-align:middle; background-color: #CCCCCC; }
    a:active, a:link, a:visited { color:#000099 }
    </style>
  </head>
  <body marginheight='0' marginwidth='0' leftmargin='0' topmargin='10' bgcolor='#EEEEEE'>
  <table cellspacing='0' cellpadding='0' width=770 align='center' border='0' height='100%'>
  <tr>
    <td valign='middle' align=center class='l'>
      <table cellspacing='1' cellpadding='0' width='100%' align='center' border='0' bgcolor='#000000'>
       <tr>
        <td>
          <table cellspacing='0' cellpadding='4' width='100%' align='center' border='0'>
          <tr>
            <td bgcolor='#666699' class='l' align='center'>À×°Á¼«¿á³¬¼¶ÂÛÌ³ LeoBBS X °²×°³ÌĞò</td>
          </tr>
          <tr>
            <td bgcolor='#8888AA' class='l' align='left'><span style='font-size:6pt;color:#8888AA'>.</span></td>
          </tr>
          <tr>
            <td valign='top' bgcolor='#FFFFFFF'><span font-family: ËÎÌå; font-size: 9pt;>
		$outputinfo<BR>
	¡¡¡¡¡î <a href=http://www.leobbs.com/leobbs/buy.asp target=_blank><B>Èç¹ûÒòÎªÄúË®Æ½ÓĞÏŞ¶øÎŞ·¨Õı³£°²×°ºÍÊ¹ÓÃ±¾ÂÛÌ³£¬Çë°´´Ë×¢²á±¾ÂÛÌ³ÉÌÒµ°æ£¬»ñµÃ°²×°Ê¹ÓÃĞ­ÖúµÈ¼¼ÊõÖ§³ÖÓë·şÎñ¡£</B></a><BR><BR>

            </td>
          </tr>
          </table>
         </td>
        </tr>
      </table>
      <BR><BR><hr width=500><font color=black>°æÈ¨ËùÓĞ£º<a href=http://www.leobbs.com target=_blank>À×°Á¿Æ¼¼</a> & <a href=http://bbs.leobbs.com target=_blank>À×°Á¼«¿á³¬¼¶ÂÛÌ³</a>¡¡¡¡Copyright 2003-2004<BR>
    </td>
   </tr>
  </table>
 </body>
</html>
~;
}

sub changemod {
    my ($cgibinpath, $noncgipath) = @_;
    opendir (DIRS, "$noncgipath");
    my @files = readdir(DIRS);
    closedir (DIRS);
    my @usrdir = grep(/^usr/i, @files);
    my $usrdir = $usrdir[0];
    $usrdir = $usrdir[1] if (lc($usrdir) eq 'usravatars');
    chmod(0777,"$noncgipath/$usrdir");
    chmod(0777,"$noncgipath/myimage");
    chmod(0777,"$noncgipath/usravatars");
    chmod(0777,"$noncgipath/face");
    chmod(0777,"$noncgipath/face/js");
    opendir (DIRS, "$cgibinpath");
    my @files = readdir(DIRS);
    closedir (DIRS);
    foreach (@files) { chmod(0777,"$cgibinpath/$_") if ($_ !~ /\./); }
    my @files1 = grep(/\.cgi/i, @files);
    foreach (@files1) { chmod(0755,"$cgibinpath/$_"); }
    @files1 = grep(/\.pl/i, @files);
    foreach (@files1) { chmod(0755,"$cgibinpath/$_"); }
    @files1 = grep(/\.pm/i, @files);
    foreach (@files1) { chmod(0755,"$cgibinpath/$_"); }
    mkdir("$cgibinpath/$memdir/old",0777) unless (-e "$cgibinpath/$memdir/old");
    chmod(0777,"$cgibinpath/$memdir/old");
    mkdir("$cgibinpath/$msgdir/in",0777) unless (-e "$cgibinpath/$msgdir/in");
    chmod(0777,"$cgibinpath/$msgdir/in");
    mkdir("$cgibinpath/$msgdir/main",0777) unless (-e "$cgibinpath/$msgdir/main");
    chmod(0777,"$cgibinpath/$msgdir/main");
    mkdir("$cgibinpath/$msgdir/out",0777) unless (-e "$cgibinpath/$msgdir/out");
    chmod(0777,"$cgibinpath/$msgdir/out");
    mkdir("$cgibinpath/$msgdir/modscarddata",0777) unless (-e "$cgibinpath/$msgdir/modscarddata");
    chmod(0777,"$cgibinpath/$msgdir/modscarddata");
    mkdir("$cgibinpath/$memfavdir/open",0777) unless (-e "$cgibinpath/$memfavdir/open");
    chmod(0777,"$cgibinpath/$memfavdir/open");
    mkdir("$cgibinpath/$memfavdir/close",0777) unless (-e "$cgibinpath/$memfavdir/close");
    chmod(0777,"$cgibinpath/$memfavdir/close");
    mkdir("$cgibinpath/verifynum",0777) unless (-e "$cgibinpath/verifynum");
    chmod(0777,"$cgibinpath/verifynum");
    mkdir("$cgibinpath/verifynum/login",0777) unless (-e "$cgibinpath/verifynum/login");
    chmod(0777,"$cgibinpath/verifynum/login");
}

sub sendurlinfo {
    eval("use Socket;");
    return if ($@ ne "");
    ($host,$path,$content) = @_;
    $host =~ s/^http:\/\///isg;
    $port = 80;
    $path = "/$path" if ($path !~ /^\//);
    my ($name, $aliases, $type, $len, @thataddr, $a, $b, $c, $d, $that);
    my ($name, $aliases, $type, $len, @thataddr) = gethostbyname($host);
    my ($a, $b, $c, $d) = unpack("C4", $thataddr[0]);
    my $that = pack('S n C4 x8', 2, $port, $a, $b, $c, $d);
    return unless (socket(S, 2, 1, 0));
    select(S);
    $| = 1;
    select(STDOUT);
    return unless (connect(S, $that));
    print S "POST http://$host/$path HTTP/1.0\n";
    print S "Content-type: application/x-www-form-urlencoded\n";
    my $contentLength = length $content;
    print S "Content-length: $contentLength\n";
    print S "\n";
    print S "$content";
    @results = <S>;
    close(S);
    undef $|;
    return;
}

# ²âÊÔ¾ø¶ÔÂ·¾¶
sub mypath {
    local $temp;
    if ($ENV{'SERVER_SOFTWARE'} =~ /apache/i) {
        if ($ENV{'SCRIPT_FILENAME'}=~ /cgiwrap/i) {
            $temp=$ENV{'PATH_TRANSLATED'};
        }
        else {
            $temp=$ENV{'SCRIPT_FILENAME'};
        }
        $temp=~ s/\\/\//g if ($temp=~/\\/);
        $mypath=substr($temp,0,rindex($temp,"/"));
    }
    else {
    	$ENV{'PATH_TRANSLATED'} = $ENV{'SCRIPT_FILENAME'} if ($ENV{'PATH_TRANSLATED'} eq "");
        $mypath=substr($ENV{'PATH_TRANSLATED'},0,rindex($ENV{'PATH_TRANSLATED'},"\\"));
        $mypath=~ s/\\/\//g;
    }
    return $mypath;
}

# ²âÊÔ URL Â·¾¶
sub myurl {
    local $server_port,$fullurl,$scheme,$default_port,$request_port;
    $scheme = 'http';
    if (($ENV{'HTTPS'} =~ /^(on|1)$/i)
        || ($ENV{'REQUEST_SCHEME'} =~ /^https$/i)
        || ($ENV{'HTTP_X_FORWARDED_PROTO'} =~ /^https$/i)
        || ($ENV{'HTTP_FRONT_END_HTTPS'} =~ /^(on|1)$/i)) {
        $scheme = 'https';
    }
    $default_port = $scheme eq 'https' ? '443' : '80';
    if ($ENV{'HTTP_X_FORWARDED_HOST'} ne "") {
        ($fullurl) = split(/\s*,\s*/, $ENV{'HTTP_X_FORWARDED_HOST'});
    } elsif ($ENV{'HTTP_HOST'} ne "") {
        $fullurl = $ENV{'HTTP_HOST'};
    } else {
        $fullurl = $ENV{'SERVER_NAME'};
    }
    $request_port = $ENV{'HTTP_X_FORWARDED_PORT'};
    $server_port = ":$request_port" if (($request_port ne '')&&($request_port ne $default_port));
    $fullurl = "$fullurl$server_port" if (($server_port ne '')&&($fullurl !~ /\:/));
    $fullurl = "$scheme://$fullurl$ENV{'SCRIPT_NAME'}";
    $myurl   = substr($fullurl,0,rindex($fullurl,"/"));
    return $myurl;
}

# ²âÊÔÍ¼ÏñÄ¿Â¼µÄ¾ø¶ÔÂ·¾¶ºÍ url Â·¾¶
sub myimgdir {
  my $html_dir = $html_url = $base = $base1 = "";
  $base  = $mypath;
  $base1 = $myurl;
    if (-e "$base/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/non-cgi";
	$html_url = "$base1/non-cgi";
    } elsif (-e "$base/lb5000/editor/selcolor.html") {
	$html_dir = "$base/lb5000";
	$html_url = "$base1/lb5000";
    } elsif (-e "$base/ib2000/editor/selcolor.html") {
	$html_dir = "$base/ib2000";
	$html_url = "$base1/ib2000";
    } elsif (-e "$base/lb/editor/selcolor.html") {
	$html_dir = "$base/lb";
	$html_url = "$base1/lb";
    } elsif (-e "$base/ib/editor/selcolor.html") {
	$html_dir = "$base/ib";
	$html_url = "$base1/ib";
    } elsif (-e "$base/bbs/editor/selcolor.html") {
	$html_dir = "$base/bbs";
	$html_url = "$base1/bbs";
    } elsif (-e "$base/leobbs/editor/selcolor.html") {
	$html_dir = "$base/leobbs";
	$html_url = "$base1/leobbs";
    } elsif (-e "$base/leo/editor/selcolor.html") {
	$html_dir = "$base/leo";
	$html_url = "$base1/leo";
    } elsif (-e "$base/non-cgi/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/non-cgi";
	$html_url = "$base1/non-cgi/non-cgi";
    } elsif (-e "$base/lb5000/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/lb5000/non-cgi";
	$html_url = "$base1/lb5000/non-cgi";
    } elsif (-e "$base/ib2000/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/ib2000/non-cgi";
	$html_url = "$base1/ib2000/non-cgi";
    } elsif (-e "$base/lb/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/lb/non-cgi";
	$html_url = "$base1/lb/non-cgi";
    } elsif (-e "$base/ib/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/ib/non-cgi";
	$html_url = "$base1/ib/non-cgi";
    } elsif (-e "$base/bbs/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/bbs/non-cgi";
	$html_url = "$base1/bbs/non-cgi";
    } elsif (-e "$base/leobbs/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/leobbs/non-cgi";
	$html_url = "$base1/leobbs/non-cgi";
    } elsif (-e "$base/leo/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/leo/non-cgi";
	$html_url = "$base1/leo/non-cgi";
    } elsif (-e "$base/non-cgi/bbs/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/bbs";
	$html_url = "$base1/non-cgi/bbs";
    } elsif (-e "$base/non-cgi/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/non-cgi";
	$html_url = "$base1/non-cgi/non-cgi";
    } elsif (-e "$base/non-cgi/lb/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/lb";
	$html_url = "$base1/non-cgi/lb";
    } elsif (-e "$base/non-cgi/lb5000/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/lb5000";
	$html_url = "$base1/non-cgi/lb5000";
    } elsif (-e "$base/non-cgi/ib2000/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/ib2000";
	$html_url = "$base1/non-cgi/ib2000";
    } elsif (-e "$base/non-cgi/ib/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/ib";
	$html_url = "$base1/non-cgi/ib";
    } elsif (-e "$base/non-cgi/leo/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/leo";
	$html_url = "$base1/non-cgi/leo";
    } elsif (-e "$base/non-cgi/leobbs/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/leobbs";
	$html_url = "$base1/non-cgi/leobbs";
    } elsif (-e "$base/htdocs/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi";
	$html_url = "$base1/non-cgi";
    } elsif (-e "$base/htdocs/lb5000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/lb5000";
	$html_url = "$base1/lb5000";
    } elsif (-e "$base/htdocs/ib2000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/ib2000";
	$html_url = "$base1/ib2000";
    } elsif (-e "$base/htdocs/lb/editor/selcolor.html") {
	$html_dir = "$base/htdocs/lb";
	$html_url = "$base1/lb";
    } elsif (-e "$base/htdocs/ib/editor/selcolor.html") {
	$html_dir = "$base/htdocs/ib";
	$html_url = "$base1/ib";
    } elsif (-e "$base/htdocs/bbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/bbs";
	$html_url = "$base1/bbs";
    } elsif (-e "$base/htdocs/leobbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/leobbs";
	$html_url = "$base1/leobbs";
    } elsif (-e "$base/htdocs/leo/editor/selcolor.html") {
	$html_dir = "$base/htdocs/leo";
	$html_url = "$base1/leo";
    } elsif (-e "$base/htdocs/non-cgi/bbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/bbs";
	$html_url = "$base1/non-cgi/bbs";
    } elsif (-e "$base/htdocs/non-cgi/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/non-cgi";
	$html_url = "$base1/non-cgi/non-cgi";
    } elsif (-e "$base/htdocs/non-cgi/lb/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/lb";
	$html_url = "$base1/non-cgi/lb";
    } elsif (-e "$base/htdocs/non-cgi/lb5000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/lb5000";
	$html_url = "$base1/non-cgi/lb5000";
    } elsif (-e "$base/htdocs/non-cgi/ib2000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/ib2000";
	$html_url = "$base1/non-cgi/ib2000";
    } elsif (-e "$base/htdocs/non-cgi/ib/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/ib";
	$html_url = "$base1/non-cgi/ib";
    } elsif (-e "$base/htdocs/non-cgi/leo/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/leo";
	$html_url = "$base1/non-cgi/leo";
    } elsif (-e "$base/htdocs/non-cgi/leobbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/leobbs";
	$html_url = "$base1/non-cgi/leobbs";
    }

  if (($html_dir eq "")||(!(-e "$html_dir/images/board.js"))) {
    if ($base =~ m|(.*)/(.+?)|) { $base  = $1; } else { $base  = $mypath; }
    if ($base1 =~ m|(.*)/(.+?)|)  { $base1 = $1; } else { $base1 = $myurl;  }
    if (-e "$base/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/non-cgi";
	$html_url = "$base1/non-cgi";
    } elsif (-e "$base/lb5000/editor/selcolor.html") {
	$html_dir = "$base/lb5000";
	$html_url = "$base1/lb5000";
    } elsif (-e "$base/ib2000/editor/selcolor.html") {
	$html_dir = "$base/ib2000";
	$html_url = "$base1/ib2000";
    } elsif (-e "$base/lb/editor/selcolor.html") {
	$html_dir = "$base/lb";
	$html_url = "$base1/lb";
    } elsif (-e "$base/ib/editor/selcolor.html") {
	$html_dir = "$base/ib";
	$html_url = "$base1/ib";
    } elsif (-e "$base/bbs/editor/selcolor.html") {
	$html_dir = "$base/bbs";
	$html_url = "$base1/bbs";
    } elsif (-e "$base/leobbs/editor/selcolor.html") {
	$html_dir = "$base/leobbs";
	$html_url = "$base1/leobbs";
    } elsif (-e "$base/leo/editor/selcolor.html") {
	$html_dir = "$base/leo";
	$html_url = "$base1/leo";
    } elsif (-e "$base/non-cgi/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/non-cgi";
	$html_url = "$base1/non-cgi/non-cgi";
    } elsif (-e "$base/lb5000/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/lb5000/non-cgi";
	$html_url = "$base1/lb5000/non-cgi";
    } elsif (-e "$base/ib2000/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/ib2000/non-cgi";
	$html_url = "$base1/ib2000/non-cgi";
    } elsif (-e "$base/lb/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/lb/non-cgi";
	$html_url = "$base1/lb/non-cgi";
    } elsif (-e "$base/ib/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/ib/non-cgi";
	$html_url = "$base1/ib/non-cgi";
    } elsif (-e "$base/bbs/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/bbs/non-cgi";
	$html_url = "$base1/bbs/non-cgi";
    } elsif (-e "$base/leobbs/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/leobbs/non-cgi";
	$html_url = "$base1/leobbs/non-cgi";
    } elsif (-e "$base/leo/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/leo/non-cgi";
	$html_url = "$base1/leo/non-cgi";
    } elsif (-e "$base/non-cgi/bbs/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/bbs";
	$html_url = "$base1/non-cgi/bbs";
    } elsif (-e "$base/non-cgi/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/non-cgi";
	$html_url = "$base1/non-cgi/non-cgi";
    } elsif (-e "$base/non-cgi/lb/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/lb";
	$html_url = "$base1/non-cgi/lb";
    } elsif (-e "$base/non-cgi/lb5000/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/lb5000";
	$html_url = "$base1/non-cgi/lb5000";
    } elsif (-e "$base/non-cgi/ib2000/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/ib2000";
	$html_url = "$base1/non-cgi/ib2000";
    } elsif (-e "$base/non-cgi/ib/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/ib";
	$html_url = "$base1/non-cgi/ib";
    } elsif (-e "$base/non-cgi/leo/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/leo";
	$html_url = "$base1/non-cgi/leo";
    } elsif (-e "$base/non-cgi/leobbs/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/leobbs";
	$html_url = "$base1/non-cgi/leobbs";
    } elsif (-e "$base/htdocs/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi";
	$html_url = "$base1/non-cgi";
    } elsif (-e "$base/htdocs/lb5000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/lb5000";
	$html_url = "$base1/lb5000";
    } elsif (-e "$base/htdocs/ib2000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/ib2000";
	$html_url = "$base1/ib2000";
    } elsif (-e "$base/htdocs/lb/editor/selcolor.html") {
	$html_dir = "$base/htdocs/lb";
	$html_url = "$base1/lb";
    } elsif (-e "$base/htdocs/ib/editor/selcolor.html") {
	$html_dir = "$base/htdocs/ib";
	$html_url = "$base1/ib";
    } elsif (-e "$base/htdocs/bbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/bbs";
	$html_url = "$base1/bbs";
    } elsif (-e "$base/htdocs/leobbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/leobbs";
	$html_url = "$base1/leobbs";
    } elsif (-e "$base/htdocs/leo/editor/selcolor.html") {
	$html_dir = "$base/htdocs/leo";
	$html_url = "$base1/leo";
    } elsif (-e "$base/htdocs/non-cgi/bbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/bbs";
	$html_url = "$base1/non-cgi/bbs";
    } elsif (-e "$base/htdocs/non-cgi/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/non-cgi";
	$html_url = "$base1/non-cgi/non-cgi";
    } elsif (-e "$base/htdocs/non-cgi/lb/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/lb";
	$html_url = "$base1/non-cgi/lb";
    } elsif (-e "$base/htdocs/non-cgi/lb5000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/lb5000";
	$html_url = "$base1/non-cgi/lb5000";
    } elsif (-e "$base/htdocs/non-cgi/ib2000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/ib2000";
	$html_url = "$base1/non-cgi/ib2000";
    } elsif (-e "$base/htdocs/non-cgi/ib/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/ib";
	$html_url = "$base1/non-cgi/ib";
    } elsif (-e "$base/htdocs/non-cgi/leo/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/leo";
	$html_url = "$base1/non-cgi/leo";
    } elsif (-e "$base/htdocs/non-cgi/leobbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/leobbs";
	$html_url = "$base1/non-cgi/leobbs";
    }
  }
  if (($html_dir eq "")||(!(-e "$html_dir/images/board.js"))) {
    if ($base =~ m|(.*)/(.+?)|) { $base  = $1; } else { $base  = $mypath; }
    if ($base1 =~ m|(.*)/(.+?)|)  { $base1 = $1; } else { $base1 = $myurl;  }
    if (-e "$base/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/non-cgi";
	$html_url = "$base1/non-cgi";
    } elsif (-e "$base/lb5000/editor/selcolor.html") {
	$html_dir = "$base/lb5000";
	$html_url = "$base1/lb5000";
    } elsif (-e "$base/ib2000/editor/selcolor.html") {
	$html_dir = "$base/ib2000";
	$html_url = "$base1/ib2000";
    } elsif (-e "$base/lb/editor/selcolor.html") {
	$html_dir = "$base/lb";
	$html_url = "$base1/lb";
    } elsif (-e "$base/ib/editor/selcolor.html") {
	$html_dir = "$base/ib";
	$html_url = "$base1/ib";
    } elsif (-e "$base/bbs/editor/selcolor.html") {
	$html_dir = "$base/bbs";
	$html_url = "$base1/bbs";
    } elsif (-e "$base/leobbs/editor/selcolor.html") {
	$html_dir = "$base/leobbs";
	$html_url = "$base1/leobbs";
    } elsif (-e "$base/leo/editor/selcolor.html") {
	$html_dir = "$base/leo";
	$html_url = "$base1/leo";
    } elsif (-e "$base/non-cgi/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/non-cgi";
	$html_url = "$base1/non-cgi/non-cgi";
    } elsif (-e "$base/lb5000/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/lb5000/non-cgi";
	$html_url = "$base1/lb5000/non-cgi";
    } elsif (-e "$base/ib2000/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/ib2000/non-cgi";
	$html_url = "$base1/ib2000/non-cgi";
    } elsif (-e "$base/lb/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/lb/non-cgi";
	$html_url = "$base1/lb/non-cgi";
    } elsif (-e "$base/ib/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/ib/non-cgi";
	$html_url = "$base1/ib/non-cgi";
    } elsif (-e "$base/bbs/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/bbs/non-cgi";
	$html_url = "$base1/bbs/non-cgi";
    } elsif (-e "$base/leobbs/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/leobbs/non-cgi";
	$html_url = "$base1/leobbs/non-cgi";
    } elsif (-e "$base/leo/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/leo/non-cgi";
	$html_url = "$base1/leo/non-cgi";
    } elsif (-e "$base/non-cgi/bbs/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/bbs";
	$html_url = "$base1/non-cgi/bbs";
    } elsif (-e "$base/non-cgi/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/non-cgi";
	$html_url = "$base1/non-cgi/non-cgi";
    } elsif (-e "$base/non-cgi/lb/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/lb";
	$html_url = "$base1/non-cgi/lb";
    } elsif (-e "$base/non-cgi/lb5000/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/lb5000";
	$html_url = "$base1/non-cgi/lb5000";
    } elsif (-e "$base/non-cgi/ib2000/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/ib2000";
	$html_url = "$base1/non-cgi/ib2000";
    } elsif (-e "$base/non-cgi/ib/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/ib";
	$html_url = "$base1/non-cgi/ib";
    } elsif (-e "$base/non-cgi/leo/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/leo";
	$html_url = "$base1/non-cgi/leo";
    } elsif (-e "$base/non-cgi/leobbs/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/leobbs";
	$html_url = "$base1/non-cgi/leobbs";
    } elsif (-e "$base/htdocs/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi";
	$html_url = "$base1/non-cgi";
    } elsif (-e "$base/htdocs/lb5000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/lb5000";
	$html_url = "$base1/lb5000";
    } elsif (-e "$base/htdocs/ib2000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/ib2000";
	$html_url = "$base1/ib2000";
    } elsif (-e "$base/htdocs/lb/editor/selcolor.html") {
	$html_dir = "$base/htdocs/lb";
	$html_url = "$base1/lb";
    } elsif (-e "$base/htdocs/ib/editor/selcolor.html") {
	$html_dir = "$base/htdocs/ib";
	$html_url = "$base1/ib";
    } elsif (-e "$base/htdocs/bbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/bbs";
	$html_url = "$base1/bbs";
    } elsif (-e "$base/htdocs/leobbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/leobbs";
	$html_url = "$base1/leobbs";
    } elsif (-e "$base/htdocs/leo/editor/selcolor.html") {
	$html_dir = "$base/htdocs/leo";
	$html_url = "$base1/leo";
    } elsif (-e "$base/htdocs/non-cgi/bbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/bbs";
	$html_url = "$base1/non-cgi/bbs";
    } elsif (-e "$base/htdocs/non-cgi/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/non-cgi";
	$html_url = "$base1/non-cgi/non-cgi";
    } elsif (-e "$base/htdocs/non-cgi/lb/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/lb";
	$html_url = "$base1/non-cgi/lb";
    } elsif (-e "$base/htdocs/non-cgi/lb5000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/lb5000";
	$html_url = "$base1/non-cgi/lb5000";
    } elsif (-e "$base/htdocs/non-cgi/ib2000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/ib2000";
	$html_url = "$base1/non-cgi/ib2000";
    } elsif (-e "$base/htdocs/non-cgi/ib/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/ib";
	$html_url = "$base1/non-cgi/ib";
    } elsif (-e "$base/htdocs/non-cgi/leo/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/leo";
	$html_url = "$base1/non-cgi/leo";
    } elsif (-e "$base/htdocs/non-cgi/leobbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/leobbs";
	$html_url = "$base1/non-cgi/leobbs";
    }
  }
  if (($html_dir eq "")||(!(-e "$html_dir/images/board.js"))) {
    if ($base =~ m|(.*)/(.+?)|) { $base  = $1; } else { $base  = $mypath; }
    if ($base1 =~ m|(.*)/(.+?)|)  { $base1 = $1; } else { $base1 = $myurl;  }
    if (-e "$base/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/non-cgi";
	$html_url = "$base1/non-cgi";
    } elsif (-e "$base/lb5000/editor/selcolor.html") {
	$html_dir = "$base/lb5000";
	$html_url = "$base1/lb5000";
    } elsif (-e "$base/ib2000/editor/selcolor.html") {
	$html_dir = "$base/ib2000";
	$html_url = "$base1/ib2000";
    } elsif (-e "$base/lb/editor/selcolor.html") {
	$html_dir = "$base/lb";
	$html_url = "$base1/lb";
    } elsif (-e "$base/ib/editor/selcolor.html") {
	$html_dir = "$base/ib";
	$html_url = "$base1/ib";
    } elsif (-e "$base/bbs/editor/selcolor.html") {
	$html_dir = "$base/bbs";
	$html_url = "$base1/bbs";
    } elsif (-e "$base/leobbs/editor/selcolor.html") {
	$html_dir = "$base/leobbs";
	$html_url = "$base1/leobbs";
    } elsif (-e "$base/leo/editor/selcolor.html") {
	$html_dir = "$base/leo";
	$html_url = "$base1/leo";
    } elsif (-e "$base/non-cgi/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/non-cgi";
	$html_url = "$base1/non-cgi/non-cgi";
    } elsif (-e "$base/lb5000/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/lb5000/non-cgi";
	$html_url = "$base1/lb5000/non-cgi";
    } elsif (-e "$base/ib2000/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/ib2000/non-cgi";
	$html_url = "$base1/ib2000/non-cgi";
    } elsif (-e "$base/lb/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/lb/non-cgi";
	$html_url = "$base1/lb/non-cgi";
    } elsif (-e "$base/ib/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/ib/non-cgi";
	$html_url = "$base1/ib/non-cgi";
    } elsif (-e "$base/bbs/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/bbs/non-cgi";
	$html_url = "$base1/bbs/non-cgi";
    } elsif (-e "$base/leobbs/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/leobbs/non-cgi";
	$html_url = "$base1/leobbs/non-cgi";
    } elsif (-e "$base/leo/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/leo/non-cgi";
	$html_url = "$base1/leo/non-cgi";
    } elsif (-e "$base/non-cgi/bbs/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/bbs";
	$html_url = "$base1/non-cgi/bbs";
    } elsif (-e "$base/non-cgi/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/non-cgi";
	$html_url = "$base1/non-cgi/non-cgi";
    } elsif (-e "$base/non-cgi/lb/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/lb";
	$html_url = "$base1/non-cgi/lb";
    } elsif (-e "$base/non-cgi/lb5000/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/lb5000";
	$html_url = "$base1/non-cgi/lb5000";
    } elsif (-e "$base/non-cgi/ib2000/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/ib2000";
	$html_url = "$base1/non-cgi/ib2000";
    } elsif (-e "$base/non-cgi/ib/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/ib";
	$html_url = "$base1/non-cgi/ib";
    } elsif (-e "$base/non-cgi/leo/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/leo";
	$html_url = "$base1/non-cgi/leo";
    } elsif (-e "$base/non-cgi/leobbs/editor/selcolor.html") {
	$html_dir = "$base/non-cgi/leobbs";
	$html_url = "$base1/non-cgi/leobbs";
    } elsif (-e "$base/htdocs/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi";
	$html_url = "$base1/non-cgi";
    } elsif (-e "$base/htdocs/lb5000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/lb5000";
	$html_url = "$base1/lb5000";
    } elsif (-e "$base/htdocs/ib2000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/ib2000";
	$html_url = "$base1/ib2000";
    } elsif (-e "$base/htdocs/lb/editor/selcolor.html") {
	$html_dir = "$base/htdocs/lb";
	$html_url = "$base1/lb";
    } elsif (-e "$base/htdocs/ib/editor/selcolor.html") {
	$html_dir = "$base/htdocs/ib";
	$html_url = "$base1/ib";
    } elsif (-e "$base/htdocs/bbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/bbs";
	$html_url = "$base1/bbs";
    } elsif (-e "$base/htdocs/leobbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/leobbs";
	$html_url = "$base1/leobbs";
    } elsif (-e "$base/htdocs/leo/editor/selcolor.html") {
	$html_dir = "$base/htdocs/leo";
	$html_url = "$base1/leo";
    } elsif (-e "$base/htdocs/non-cgi/bbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/bbs";
	$html_url = "$base1/non-cgi/bbs";
    } elsif (-e "$base/htdocs/non-cgi/non-cgi/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/non-cgi";
	$html_url = "$base1/non-cgi/non-cgi";
    } elsif (-e "$base/htdocs/non-cgi/lb/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/lb";
	$html_url = "$base1/non-cgi/lb";
    } elsif (-e "$base/htdocs/non-cgi/lb5000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/lb5000";
	$html_url = "$base1/non-cgi/lb5000";
    } elsif (-e "$base/htdocs/non-cgi/ib2000/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/ib2000";
	$html_url = "$base1/non-cgi/ib2000";
    } elsif (-e "$base/htdocs/non-cgi/ib/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/ib";
	$html_url = "$base1/non-cgi/ib";
    } elsif (-e "$base/htdocs/non-cgi/leo/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/leo";
	$html_url = "$base1/non-cgi/leo";
    } elsif (-e "$base/htdocs/non-cgi/leobbs/editor/selcolor.html") {
	$html_dir = "$base/htdocs/non-cgi/leobbs";
	$html_url = "$base1/non-cgi/leobbs";
    }
  }
  $html_dir = $mypath if ($html_dir eq "");
  $html_url = $myurl  if ($html_url eq "");
  return "$html_dir|$html_url|";
}

sub changedirname {
    opendir (DIRS, "$lbdir");
    my @files = readdir(DIRS);
    closedir (DIRS);
    @files = grep(/^\w+?$/i, @files);
    my @searchdir = grep(/^search/i, @files);
    my $searchdir = $searchdir[0];
    my @memdir = grep(/^members/i, @files);
    my $memdir = $memdir[0];
    my @msgdir = grep(/^messages/i, @files);
    my $msgdir = $msgdir[0];
    my @memfavdir = grep(/^memfav/i, @files);
    my $memfavdir = $memfavdir[0];
    my @recorddir = grep(/^record/i, @files);
    my $recorddir = $recorddir[0];
    my @saledir = grep(/^sale/i, @files);
    my $saledir = $saledir[0];
   my @ftpdir = grep(/^ftpdata/i, @files);
   my $ftpdir = $ftpdir[0];
   opendir(DIRS, $imagesdir);
   my @files = readdir(DIRS);
   closedir(DIRS);
   @files = grep(/^\w+?$/i, @files);
   my @usrdir = grep(/^usr/i, @files);
   my $usrdir = $usrdir[0];
   $usrdir = $usrdir[1] if (lc($usrdir) eq 'usravatars');

	my $x = &myrand(1000000000);
	$x = crypt($x, aun);
	$x =~ s/%([a-fA-F0-9]{2})/pack("C", hex($1))/eg;
	$x =~ s/[^\w\d]//g;
	$x = substr($x, 2, 9);
	$usrdir    = "usr$x"      if (rename("$imagesdir$usrdir", "${imagesdir}usr$x"));
	$recorddir = "record$x"   if (rename("$lbdir$recorddir",  "${lbdir}record$x"));
	$saledir = "sale$x"   if (rename("$lbdir$saledir",  "${lbdir}sale$x"));

	my $x = &myrand(1000000000);
	$x = crypt($x, aun);
	$x =~ s/%([a-fA-F0-9]{2})/pack("C", hex($1))/eg;
	$x =~ s/[^\w\d]//g;
	$x = substr($x, 2, 9);
	$memdir    = "members$x"  if (rename("$lbdir$memdir",     "${lbdir}members$x"));
	$msgdir    = "messages$x" if (rename("$lbdir$msgdir",     "${lbdir}messages$x"));

	my $x = &myrand(1000000000);
	$x = crypt($x, aun);
	$x =~ s/%([a-fA-F0-9]{2})/pack("C", hex($1))/eg;
	$x =~ s/[^\w\d]//g;
	$x = substr($x, 2, 9);
	$searchdir = "search$x"   if (rename("$lbdir$searchdir",  "${lbdir}search$x"));
	$ftpdir    = "ftpdata$x"  if (rename("$lbdir$ftpdir",     "${lbdir}ftpdata$x"));
	$memfavdir = "memfav$x"   if (rename("$lbdir$memfavdir",  "${lbdir}memfav$x"));
}
