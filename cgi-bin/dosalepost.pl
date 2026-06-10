#####################################################
#  LEO SuperCool BBS / LeoBBS X / 雷傲极酷超级论坛  #
#####################################################
# 基于山鹰(糊)、花无缺制作的 LB5000 XP 2.30 免费版  #
#   新版程序制作 & 版权所有: 雷傲科技 (C)(R)2004    #
#####################################################
#      主页地址： http://www.LeoBBS.com/            #
#      论坛地址： http://bbs.LeoBBS.com/            #
#####################################################

sub dosalepost {
	    require "data/cityinfo.cgi" if ($addmoney eq "" || $replymoney eq "" || $moneyname eq "");
    	    my $postno = $rn;
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
            { @allexege = ($$post =~ /\[buyexege\].*?\[\/buyexege\]/ig); }
            unless ((lc($inmembername) eq lc($membername))||($mymembercode eq "ad")||($mymembercode eq 'smo')||($myinmembmod eq "yes")||($isbuyer eq "yes")) {
                $$post=qq~<FONT COLOR=$fonthighlight><B>[Sale Post: Money $1]</B></FONT><BR>  <BR><FONT COLOR=$posternamecolor>[查看这个帖子需要 <b>$1</b> $moneyname，目前已有 <B>$allbuyerno</B> 人购买]</FONT><BR><br><script>function salesubmitonce(theform){if (document.all||document.getElementById){for (i=0;i<theform.length;i++){ var tempobj=theform.elements[i]; if(tempobj.type.toLowerCase()=="submit"||tempobj.type.toLowerCase()=="reset") { tempobj.disabled=true; }}}}</script>
                <FORM action=buypost.cgi method=post onSubmit="salesubmitonce(this)"><input name=inforum type=hidden value=$inforum><input name=intopic type=hidden value=$intopic><input name=postnumber type=hidden value=$postno><input name=salemembername type=hidden value="$membername"><input name=moneynumber type=hidden value=$1><INPUT name=B1 type=submit value="算你狠。。我买，我付钱"></form><BR> ~;
                $$post .= join ('<BR>', @allexege);
                $addme="附件保密!<br><br>" if ($addme);
	    } else {
	    	$buyeroutput = "";
	    	if ((lc($inmembername) eq lc($membername))||($mymembercode eq "ad")||($mymembercode eq 'smo')||($myinmembmod eq "yes")) {
                    if ($allbuyerno > 0 ) {
	                $buyeroutput = qq~<SCRIPT LANGUAGE="JavaScript">function surfto(list) { var myindex1  = list.selectedIndex; if (myindex1 != 0 & myindex1 != 1) { var newwindow = list.options[myindex1].value; var msgwindow = window.open("profile.cgi?action=show&member=" + newwindow,"",""); } }</SCRIPT><img src=$imagesurl/images/team2.gif width=19 height=19 align=absmiddle><select onchange="surfto(this)">
<option>购买名单：</option><option>------------</option>
~;
	                foreach (@allbuyer) {
	                    chomp $_;
	                    next if ($_ eq "");
	                    my $cleanedmodname = $_;
	                    $cleanedmodname =~ s/ /\_/g;
	                    $cleanedmodname =~ tr/A-Z/a-z/;
	                    $cleanedmodname = uri_escape($cleanedmodname);
    	                    $buyeroutput .= qq~<option value="$cleanedmodname">$_</option>~;
	                }
	                $buyeroutput .= qq~</select></form><BR>\n~;
                    }
                }
	        $$post=~s/LBSALE\[(.*?)\]LBSALE/$buyeroutput<font color=$fonthighlight>（此贴售价 <B>$1<\/B> $moneyname，目前已有 <B>$allbuyerno<\/B> 人购买）<\/font><br><br>/sg;   
	    }
	    $$post =~ s/\[buyexege\](.*?)\[\/buyexege\]/<blockquote><font color=$posternamecolor>买卖文章注解内容： <hr noshade size=1>$1<hr noshade size=1><\/blockquote><\/font>/g;
	}
1;
