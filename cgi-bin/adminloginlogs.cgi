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
require "admin.lib.pl";
require "data/boardinfo.cgi";
require "bbs.lib.pl";
$|++;

$thisprog = "adminloginlogs.cgi";
eval ('$complevel = 9 if ($complevel eq ""); use WebGzip($complevel); $gzipused = 1;') if ($usegzip eq "yes");

$query = new LBCGI;

$action        = $query -> param("action");
$action        = &cleaninput("$action");

$inmembername = $query->cookie("adminname");
$inpassword   = $query->cookie("adminpass");
$inmembername =~ s/[\a\f\n\e\0\r\t\`\~\!\@\#\$\%\^\&\*\(\)\+\=\\\{\}\;\'\:\"\,\.\/\<\>\?]//isg;
$inpassword =~ s/[\a\f\n\e\0\r\t\|\@\;\#\{\}\$]//isg;

&getadmincheck;
print header(-charset=>gb2312 , -expires=>"$EXP_MODE" , -cache=>"$CACHE_MODES");

&admintitle;
            

if ($action eq "process") {
        
        &getmember("$inmembername","no");
        
                if (($membercode eq "ad") && ($inpassword eq $password) && (lc($inmembername) eq lc($membername))) { 

                $filetoopen = "$lbdir" . "data/adminlogin.cgi";
                open (FILE, "$filetoopen");
                @baddel = <FILE>;
                close (FILE);
		$baddels = @baddel;
		
		if ($baddels > 50) { $baddels = 50; }

                open (FILE, ">$filetoopen");
                for ($i=0;$i<$baddels;$i++) {
                    $j=$i-$baddels;
                    $info = $baddel[$j];
                    chomp $info;
                    print FILE "$info\n";
                }
                close (FILE);


           print qq~
           <tr><td bgcolor=#2159C9><font color=#FFFFFF>
		<b>欢迎来到论坛管理中心 / 删除日志</b>
		</td></tr>
		<tr>
		<td bgcolor=#EEEEEE valign=middle align=center>
		<font color=#333333><b>文件删除操作日志</b>
		</td></tr>
		<tr><td align=center><br><br>除了最后50条记录，其他早期的安全日志纪录已经删除!</td></tr>
           ~;
         
                }
        
        }
        
    else {
        
        &getmember("$inmembername","no");
        
        if (($membercode eq "ad") && ($inpassword eq $password) && (lc($inmembername) eq lc($membername))) {

                $filetoopen = "$lbdir" . "data/adminlogin.cgi";
                open (FILE, "$filetoopen");
                @baddel = <FILE>;
                close (FILE);

		my $key = $query->param('key');
		my $type = $query->param('type');
		if ($key ne "")
		{
			if ($type eq "time")
			{
				my ($begin, $end);
				for ($begin = 0; $begin < @baddel; $begin++)
				{
					my ($temp1, $temp2, $temp3, $temp4, $temp5, $temptime) = split(/\t/, $baddel[$begin]);
					$temptime = &shortdate($temptime + $timezone * 3600 + $timedifferencevalue * 3600);
					last if ($key eq $temptime);
				}
				for ($end = @baddel - 1; $end >= $begin - 1; $end--)
				{
					my ($temp1, $temp2, $temp3, $temp4, $temp5, $temptime) = split(/\t/, $baddel[$end]);
					$temptime = &shortdate($temptime + $timezone * 3600 + $timedifferencevalue * 3600);
					last if ($key eq $temptime);
				}
				if ($begin > $end)
				{
					undef(@baddel);
				}
				else
				{
					@baddel = @baddel[$begin..$end];
				}
			}
			else
			{
				@baddel = grep(/^$key\t/i, @baddel);
			}
		}
                my $page = $query->param('page');
                $page = 1 unless($page);
		my $allnum = @baddel;
		my $temp = $allnum / 12;
		my $allpages = int($temp);
		$allpages++ if ($allpages != $temp);
		$page = 1 if ($page < 1);
		$page = $allpages if ($page > $allpages);
		my $showpage = "";
		if (!$allpages)
		{
			$showpage .= "当前没有记录";
		}
		elsif ($allpages == 1)
		{
			$showpage .= "当前记录只有 1 页";
		}
		else
		{
			$showpage .= qq~记录共 <b>$allpages</b> 页 ~;
			$i = $page - 1;
			$showpage .= qq~<span style="cursor:hand" OnClick="MAINFORM.page.value=$i; MAINFORM.submit();" title="上一页"><<</span> ~ if ($i > 0);
			$showpage .= "[ ";
			$i = $page - 3;
			$showpage .= qq~<span style="cursor:hand" OnClick="MAINFORM.page.value=$i; MAINFORM.submit();">←</span> ~ if ($i > 0);
			$i++;
			$showpage .= qq~<span style="cursor:hand" OnClick="MAINFORM.page.value=$i; MAINFORM.submit();">$i</span> ~ if ($i > 0);
			$i++;
			$showpage .= qq~<span style="cursor:hand" OnClick="MAINFORM.page.value=$i; MAINFORM.submit();">$i</span> ~ if ($i > 0);
			$i++;
			$showpage .= qq~<font color=#990000>$i</font> ~;
			$i++;
			$showpage .= qq~<span style="cursor:hand" OnClick="MAINFORM.page.value=$i; MAINFORM.submit();">$i</span> ~ if ($i <= $allpages);
			$i++;
			$showpage .= qq~<span style="cursor:hand" OnClick="MAINFORM.page.value=$i; MAINFORM.submit();">$i</span> ~ if ($i <= $allpages);
			$i++;
			$showpage .= qq~<span style="cursor:hand" OnClick="MAINFORM.page.value=$i; MAINFORM.submit();">→</span> ~ if ($i <= $allpages);
			$showpage .= "] ";
			$i = $page + 1;
			$showpage .= qq~<span style="cursor:hand" OnClick="MAINFORM.page.value=$i; MAINFORM.submit();" title="下一页">>></span> ~ if ($i <= $allpages);
		}
                
                print qq(
                <tr><td bgcolor=#2159C9 colspan=6><font color=#FFFFFF>
		<b>欢迎来到论坛管理中心 / 管理区安全日志</b>
		</td></tr>
		<tr>
		<td bgcolor=#EEEEEE valign=middle align=center colspan=6>
		<font color=#333333><b>论坛安全操作日志</b>
		</td></tr>
		<tr><td>操作者</td><td>密码</td><td>IP 地址</td><td>代理 IP</td><td>操作日志</td><td>操作时间</td></tr>
		);
		if ($allnum) {
		for ($i = $allnum - $page * 12  + 11; $i >= $allnum - $page * 12 && $i >= 0; $i--) {
		(my $name, my $pass, my $ip, my $proxy, my $logs,my $oldtime) = split(/\t/,$baddel[$i]);
    		$oldtime = $oldtime + ($timedifferencevalue*3600) + ($timezone*3600);
    		$oldtime = &dateformatshort($oldtime);
    		$pass =~ s/^错//;
		print qq~
		<tr><td>$name</td><td>$pass</td><td>$ip</td><td>$proxy</td><td>$logs</td><td>$oldtime</td></tr>
		~;
		    }
		}
                my $tempoutput = qq~
                <tr>
                <form name=MAINFORM action=$thisprog method=POST><td bgcolor=#EEEEEE valign=middle colspan=2><br>
		<input type=hidden name=page value=$page><select name=type><option value="name">按操作者</option><option value="time">按特定日期</option></select> <input name=key type=text size=12 value=$key> <input type=submit value="搜寻">
		</td></form>
                <td bgcolor=#EEEEEE valign=middle align=center colspan=3><br>
		$showpage
		</td>
		<td bgcolor=#EEEEEE valign=middle><br>
		<font color=#333333><b><a href=$thisprog?action=process OnClick="return confirm('为了安全，此操作还会保留最后50条记录的。\\n真的要删除安全日志么？');">删除安全日志</a></b>
		</td></tr>
                ~;
		$tempoutput =~ s/<option value="$type">/<option value="$type" selected>/g;
		print $tempoutput;
                }
                else {
                    &adminlogin;
                    }
        }
print qq~</td></tr></table></body></html>~;
exit;
