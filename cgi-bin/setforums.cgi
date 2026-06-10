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
use File::Copy;
$loadcopymo = 1;
use Image::Info qw(image_info);
$LBCGI::POST_MAX=800000;
$LBCGI::DISABLE_UPLOADS = 0;
$LBCGI::HEADERS_ONCE = 1;
require "admin.lib.pl";
require "data/boardinfo.cgi";
require "bbs.lib.pl";
require "rebuildlist.pl";

$|++;

$thisprog = "setforums.cgi";
eval ('$complevel = 9 if ($complevel eq ""); use WebGzip($complevel); $gzipused = 1;') if ($usegzip eq "yes");

$query = new LBCGI;

#&ipbanned; #封杀一些 ip

$inmembername = $query->cookie("adminname");
$inpassword   = $query->cookie("adminpass");
$inmembername =~ s/[\a\f\n\e\0\r\t\`\~\!\@\#\$\%\^\&\*\(\)\+\=\\\{\}\;\'\:\"\,\.\/\<\>\?]//isg;
$inpassword =~ s/[\a\f\n\e\0\r\t\|\@\;\#\{\}\$]//isg;

@params = $query->param;
foreach $param(@params) {
    next unless defined $param;
    next if $param eq 'SEND_MAIL';
    $theparam = $query->param($param);
    $theparam = &cleaninput("$theparam");
    $PARAM{$param} = $theparam;
}

    $action      =  $PARAM{'action'};
    $inforum     =  $PARAM{'forum'};
    $incategory  =  $PARAM{'category'};
    $checkaction =  $PARAM{'checkaction'};
    $inmovetype     =  $PARAM{'movetype'};
    $incforum     =  $PARAM{'cforum'};

    $new_categoryname     = $PARAM{'categoryname'};
    $new_categorynumber   = $PARAM{'categorynumber'};
    $new_forumname        = $PARAM{'forumname'};
    $new_forumdescription = $PARAM{'forumdescription'};
    $new_forummoderator   = $PARAM{'forummoderator'};
    $new_forummoderator =~ s/\, /\,/gi;
    $new_forummoderator =~ s/ \,/\,/gi;
    $new_catemods        = $PARAM{'catemods'}; 
    $new_catemods        =~ s/\, /\,/gi; 
    $new_catemods        =~ s/ \,/\,/gi;
    
    $new_htmlstate        = $PARAM{'htmlstate'};
    $new_idmbcodestate    = $PARAM{'idmbcodestate'};
    $new_privateforum     = $PARAM{'privateforum'};
    $new_forumpass	  = $PARAM{'forumpass'};
    $new_hiddenforum	  = $PARAM{'hiddenforum'};
    $new_indexforum	  = $PARAM{'indexforum'};
    $new_startnewthreads  = $PARAM{'startnewthreads'};
    $new_forumgraphic     = $PARAM{'forumgraphic'};
    $new_teamlogo         = $PARAM{'teamlogo'};
    $new_teamurl          = $PARAM{'teamurl'};
    $new_fgwidth          = $PARAM{'fgwidth'};
    $new_fgwidth1         = $PARAM{'fgwidth1'};
    $new_fgheight         = $PARAM{'fgheight'};
    $new_fgheight1        = $PARAM{'fgheight1'};

&getadmincheck;
print header(-charset=>gb2312 , -expires=>"$EXP_MODE" , -cache=>"$CACHE_MODES");

&admintitle;

&getmember("$inmembername","no");

if (($membercode eq "ad") && ($inpassword eq $password) && ($password ne "") && ($inmembername ne "") && (lc($inmembername) eq lc($membername))) { #s1

            my %Mode = (
            'addforum'            =>    \&addforum,
            'processnew'          =>    \&createforum,
            'edit'                =>    \&editform,
            'doedit'              =>    \&doedit,
            'bakcat'              =>    \&bakcat,
            'upcat'               =>    \&upcat,
            'addcategory'         =>    \&catform,
            'doaddcategory'       =>    \&doaddcategory,
            'editcatname'         =>    \&editcatname,
            'reordercategories'   =>    \&reordercats,
            'updatecount'  	  =>    \&updatecount,
            'recount'             =>    \&recount,
            'reorder'             =>    \&reorder,
            'delxzb'              =>    \&delxzb,
            'delans'              =>    \&delans,
            'dellogs'             =>    \&dellogs

            );


    if($Mode{$action}) {
        $Mode{$action}->();
    }
    elsif (($action eq "delete") && ($checkaction ne "yes")) { &warning; }
    elsif (($action eq "delete") && ($checkaction eq "yes")) { &deleteforum; }
    else { &forumlist; }

}
else {
    &adminlogin;
}
print qq~</td></tr></table></body></html>~;
exit;

##################################################################################
sub dellogs {

                open (FILE, "${lbdir}boarddata/adminlog$inforum.cgi");
                @baddel = <FILE>;
                close (FILE);
		$baddels = @baddel;
		
		if ($baddels > 50) { $baddels = 50; }

                open (FILE, ">${lbdir}boarddata/adminlog$inforum.cgi");
                for ($i=0;$i<$baddels;$i++) {
                    $j=$i-$baddels;
                    $info = $baddel[$j];
                    chomp $info;
                    print FILE "$info\n";
                }
                close (FILE);
    print qq~<tr><td bgcolor=#FFFFFF align=center colspan=2>
<font color=#990000><b>删除该区的版务日志</b><p>
<font color=#333333>除了最后50条记录，其他早期的版务日志纪录已经删除!！</font>
</td></tr>
~;
}	

sub delxzb {
    unlink ("${lbdir}data/xzb$inforum.cgi");
    unlink ("${lbdir}data/xzbs$inforum.cgi");
    print qq~<tr><td bgcolor=#FFFFFF align=center colspan=2>
<font color=#990000><b>删除该区所有的小字报</b><p>
<font color=#333333>该区所有的小字报已经被删除！</font>
</td></tr>
~;
}	

sub delans {
    unlink ("${lbdir}data/news$inforum.cgi");
    print qq~<tr><td bgcolor=#FFFFFF align=center colspan=2>
<font color=#990000><b>删除该区所有的公告</b><p>
<font color=#333333>该区所有的公告已经被删除！</font>
</td></tr>
~;
}	

sub bakcat {
    $filetoopen = "$lbdir" . "data/allforums.cgi";
#    &winlock($filetoopen) if ($OS_USED eq "Nt");
    open(FILE, "$filetoopen");
#    flock(FILE, 1) if ($OS_USED eq "Unix");
    my @forums = <FILE>;
    close(FILE);
#    &winunlock($filetoopen) if ($OS_USED eq "Nt");
    my $size=@forums;

    if ($size > 0) {
        unlink ("${lbdir}data/allforums.pl");
        copy("${lbdir}data/allforums.cgi","${lbdir}data/allforums.pl");
        chmod (0666,"${lbdir}data/allforums.pl");
        print qq~<tr><td bgcolor=#2159C9 colspan=3><font color=#FFFFFF><b>欢迎来到论坛管理中心 / 论坛管理</b></td></tr>
<tr><td bgcolor=#EEEEEE align=center colspan=2><font color=#333333><b>所有分类已经备份</b><br>当前论坛 $size 个已经备份！</td></tr>
~;
    }
    else {
        print qq~<tr><td bgcolor=#2159C9 colspan=3><font color=#FFFFFF><b>欢迎来到论坛管理中心 / 论坛管理</b></td></tr>
<tr><td bgcolor=#EEEEEE align=center colspan=2><font color=#333333><b>所有分类没有备份</b><br>当前论坛分类文件没有找到，请使用重新建立论坛主界面功能一次！</td></tr>
~;
    }
}

sub upcat {
    open(FILE, "${lbdir}data/allforums.pl");
    my @forums = <FILE>;
    close(FILE);
    my $size=@forums;

    if ($size > 0) {
        unlink ("${lbdir}data/allforums.cgi");
        copy("${lbdir}data/allforums.pl","${lbdir}data/allforums.cgi");
        chmod (0666,"${lbdir}data/allforums.cgi");
        print qq~<tr><td bgcolor=#2159C9 colspan=3><font color=#FFFFFF><b>欢迎来到论坛管理中心 / 论坛管理</b></td></tr>
<tr><td bgcolor=#EEEEEE align=center colspan=2><font color=#333333><b>所有分类已经还原</b><br>当前论坛 $size 个已经还原！</td></tr>
~;
    }
    else {
        print qq~<tr><td bgcolor=#2159C9 colspan=3><font color=#FFFFFF><b>欢迎来到论坛管理中心 / 论坛管理</b></td></tr>
<tr><td bgcolor=#EEEEEE align=center colspan=2><font color=#333333><b>所有分类没有还原</b><br>当前备份分类文件没有找到，使用还原前请先备份！</td></tr>
~;
    }
    opendir (CATDIR, "${lbdir}cache");
    @dirdata = readdir(CATDIR);
    closedir (CATDIR);
    @dirdata = grep(/forumcache/,@dirdata);
    foreach (@dirdata) { unlink ("${lbdir}cache/$_"); }
}

sub updatecount {
    $filetoopen = "$lbdir" . "data/allforums.cgi";
#    &winlock($filetoopen) if ($OS_USED eq "Nt");
    open(FILE, "$filetoopen");
#    flock(FILE, 1) if ($OS_USED eq "Unix");
    my @forums = <FILE>;
    close(FILE);
#    &winunlock($filetoopen) if ($OS_USED eq "Nt");

    $totle1 = 0;
    $totle2 = 0;

    foreach (@forums) {
        chomp $_;
        (my $tempno,my $no) = split(/\t/,$_);
   	next if ($tempno !~ /^[0-9]+$/);
   	eval{ require "${lbdir}boarddata/forumposts$tempno.pl";};
	$totle1 += $threads;
	$totle2 += $posts;
    }
    require "$lbdir" . "data/boardstats.cgi";

    $filetomake = "$lbdir" . "data/boardstats.cgi";
    &winlock($filetomake) if ($OS_USED eq "Nt");
    if (open(FILE, ">$filetomake")) {
        flock(FILE, 2) if ($OS_USED eq "Unix");
        print FILE "\$lastregisteredmember = \'$lastregisteredmember\'\;\n";
        print FILE "\$totalmembers = \'$totalmembers\'\;\n";
        print FILE "\$totalthreads = \'$totle1\'\;\n";
        print FILE "\$totalposts = \'$totle2\'\;\n";
        print FILE "\n1\;";
        close (FILE);
    }
    &winunlock($filetomake) if ($OS_USED eq "Nt");

    print qq~<tr><td bgcolor=#2159C9 colspan=3><font color=#FFFFFF><b>欢迎来到论坛管理中心 / 论坛管理</b></td></tr>
<tr><td bgcolor=#EEEEEE align=center colspan=2><font color=#333333><b>所有信息已经保存</b><br>
主题总数：$totle1 篇<BR>回复总数：$totle2 篇</td></tr>
~;
}

sub forumlist {
    print qq~<tr><td bgcolor=#2159C9 colspan=3><font color=#FFFFFF><b>欢迎来到论坛管理中心 / 论坛管理</b></td></tr>
<tr><td bgcolor=#FFFFFF colspan=3><font color=#333333>
<b>１．<a href="$thisprog?action=updatecount">重新统计</a>：</b><br>对整个论坛的贴子重新统计总数，这样可以修复首页上总数显示的错误。<br><br>
</td></tr><tr><td bgcolor=#FFFFFF colspan=3><font color=#333333>
<b>２．<a href="$thisprog?action=bakcat" OnClick="return confirm('确定备份论坛分类么？');">备份论坛分类</a>/<a href="$thisprog?action=upcat" OnClick="return confirm('确定还原论坛分类么？');">还原论坛分类</a></b><br>
对整个论坛的分类进行备份，这样可以修复所有论坛丢失的情况。(论坛也会自动进行备份和恢复)<br><br>
</td></tr><tr><td bgcolor=#FFFFFF colspan=3><font color=#333333>
<b>３．注意事项：</b><br>在下面，您将看到目前所有的论坛分类。您可以编辑论坛分类名或是增加一个新的论坛到这个分类中。也可以编辑或删除目前存在的论坛。您可以对目前的分类重新进行排列。<br>
</td></tr>
~;
    $filetoopen = "$lbdir" . "data/allforums.cgi";
#    &winlock($filetoopen) if ($OS_USED eq "Nt");
    open(FILE, "$filetoopen");
#    flock(FILE, 1) if ($OS_USED eq "Unix");
    @forums = <FILE>;
    close(FILE);
#    &winunlock($filetoopen) if ($OS_USED eq "Nt");
    $a = 0;
    foreach (@forums) {
	$a  = sprintf("%09d",$a);
        chomp $_;
        ($forumid, $category, $categoryplace, $forumname, my $no) = split(/\t/,$_);
    	next if ($forumid !~ /^[0-9]+$/);
	if ($category =~ /^childforum-[0-9]+/) {
	    $topforumno=$category;
	    $topforumno=~s/^childforum-//;
            my $rearrange = ("$categoryplace\t$a\t$category\t$forumname\t$forumid\t$topforumno\t");
            push (@cforums, $rearrange);
	    next;
	}
	$categoryplace  = sprintf("%09d",$categoryplace);
        my $rearrange = ("$categoryplace\t$a\t$category\t$forumname\t$forumid\t\t");
        push (@rearrangedforums, $rearrange);
        $a++;
    }
    my @rearrangedforums1 = sort (@rearrangedforums);
    undef @rearrangedforums;
    foreach (@rearrangedforums1) {
    	chomp $_;
        ($categoryplace,my $a,$category, $forumname, $forumid) = split(/\t/,$_);
        push (@rearrangedforums, "$categoryplace\t$a\t$category\t$forumname\t$forumid\t");
        @tempcforum = grep(/\t$forumid\t$/i, @cforums);
        push (@rearrangedforums,@tempcforum);
    }
    $highest = 0;
    foreach (@rearrangedforums) {
    	chomp $_;
        ($categoryplace,my $a,$category, $forumname, $forumid, $no) = split(/\t/,$_);
        $categoryplace  = sprintf("%01d",$categoryplace);
        if ($categoryplace ne $lastcategoryplace) {
            if ($categoryplace > $highest) { $highest = $categoryplace; }
            print qq~<tr><td bgcolor=#FFFFFF colspan=3 ><font color=#333333><hr noshade></td></tr><tr><td bgcolor=#EEEEEE width=20% nowrap><font color=#333333>分类名： <b>$category</b><td bgcolor=#EEEEEE width=15% align=center nowrap><font color=#333333><a href="$thisprog?action=editcatname&category=$categoryplace">编辑分类名称</a></td><td bgcolor=#EEEEEE width=25%><font color=#333333><a href="$thisprog?action=addforum&category=$categoryplace">增加论坛到此分类中</a></font></td></td></tr>~;
        }
   	eval{ require "${lbdir}boarddata/forumposts$forumid.pl";};
        if($category =~/^childforum-[0-9]+/){
        $temp="子论坛名";$addforumline="";$addspace="　";
        }else{
        $temp="论坛名";$addforumline=qq~<BR><a href="$thisprog?action=addforum&category=childforum-$forumid">增加子论坛到此论坛中</a>~;$addspace="";
        }
       $filerequire = "$lbdir" . "data/style${forumid}.cgi"; 
       if (-e $filerequire) { 
       $mydelthisstlye = qq~ <a href="forumstyles.cgi?action=delstyle&forum=$forumid">删除该区自定义风格</a> |~; 
       $mystyle = qq~| <a href="forumstyles.cgi?action=style&forum=$forumid"><font color=red>修改该区风格</font></a>~; 
       } 
       else { 
       $mystyle = qq~| <a href="forumstyles.cgi?action=style&forum=$forumid">添加该区风格</a>~; 
       }
    
	print qq~<tr><td bgcolor=#FFFFFF colspan=3 nowrap>$addspace<font color=#333333>$temp： <b>$forumname</b>　<br>$addspace主题数： <b>$threads</b>　<-->　<font color=#333333>回复数： <b>$posts</b><br><br>$addspace<a href="$thisprog?action=edit&forum=$forumid">编辑该区</a> | <a href="$thisprog?action=recount&forum=$forumid">重新计算主题和回复数 / 修复</a> $mystyle | <a href="$thisprog?action=reorder&forum=$forumid">分区内排序该区</a><BR>$addspace<a href="$thisprog?action=delxzb&forum=$forumid">删除该区所有小字报</a> | <a href="$thisprog?action=delans&forum=$forumid">删除该区所有公告</a> | <a href="$thisprog?action=dellogs&forum=$forumid">删除该区版务日志</a> | $mydelthisstlye <a href="$thisprog?action=delete&forum=$forumid">删除该区所有资料</a>$addforumline<BR><BR></td></font></td></tr>~;
        $lastcategoryplace = $categoryplace;
	undef $mydelthisstlye; 
        undef $mystyle;
    }
    $highest++;
    print qq~<td bgcolor=#FFFFFF colspan=3 ><font color=#333333><hr noshade></td></tr>
<tr><td bgcolor=#EEEEEE colspan=3 align=center><font color=#333333>
<a href="$thisprog?action=reordercategories">论坛分类重新排序</a>　　--　　<a href="$thisprog?action=addcategory&category=$highest">增加分类(同时增加一个论坛)</a>
</font></td></tr></tr></table></td></tr></table>
~;
}

sub recount {
    mkdir ("${lbdir}forum$inforum", 0777) unless (-e "${lbdir}forum$inforum");
    my $truenumber = rebuildLIST(-Forum=>"$inforum");
    ($topiccount,$threadcount) = split (/\|/,$truenumber);
    $threadcount = 0 if (!$threadcount);
    $topiccount  = 0 if (!$topiccount);

        $filetoopen = "$lbdir" . "boarddata/listno$inforum.cgi";
        open(FILE, "$filetoopen");
        $topicid = <FILE>;
        close(FILE);
        chomp $topicid;
	my $rr = &readthreadpl($inforum,$topicid);
	(my $lastpostdate, my $topicid, my $topictitle, my $topicdescription, my $threadstate, my $threadposts, my $threadviews, my $startedby, my $startedpostdate, my $lastposter, my $posticon, my $posttemp) = split (/\t/,$rr);
            $lastforumpostdate = "$lastpostdate\%\%\%$topicid\%\%\%$topictitle";
	    $lastposter = $startedby if ($lastposter eq "");
	    $filetoopen = "";
	    if (-e "${lbdir}boarddata/foruminfo$inforum.cgi") {
                open(FILE, "+<${lbdir}boarddata/foruminfo$inforum.cgi");
                ($no, $threads, $posts, $todayforumpost, $no) = split(/\t/,<FILE>);
                close(FILE);
	        seek(FILE,0,0);
                print FILE "$lastforumpostdate\t$topiccount\t$threadcount\t$todayforumpost\t$lastposter\t\n";
                close(FILE);
            } else {
                open(FILE, ">${lbdir}boarddata/foruminfo$inforum.cgi");
                print FILE "$lastforumpostdate\t$topiccount\t$threadcount\t$todayforumpost\t$lastposter\t\n";
                close(FILE);
            }
	    open(FILE, ">${lbdir}boarddata/forumposts$inforum.pl");
	    print FILE "\$threads = $topiccount;\n\$posts = $threadcount;\n\$todayforumpost = \"$todayforumpost\";\n1;\n";
            close(FILE);

    print qq~<tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF><b>欢迎来到论坛管理中心 / 重计算主题和回复数</b>
</td></tr><tr><td bgcolor=#FFFFFF colspan=2><font color=#990000>
<center><b>论坛更新成功</b></center><p>主题数： $topiccount<p>回复数： $threadcount
</td></tr></table></td></tr></table>
~;
}

sub addforum {

        print qq~
        <tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF>
        <b>欢迎来到论坛管理中心 / 增加论坛</b>
        </td></tr>
        ~;

        $filetoopen = "$lbdir" . "data/allforums.cgi";
        &winlock($filetoopen) if ($OS_USED eq "Nt");
        open(FILE, "$filetoopen");
        flock(FILE, 1) if ($OS_USED eq "Unix");
        @forums = <FILE>;
        close(FILE);
        &winunlock($filetoopen) if ($OS_USED eq "Nt");


# Find the category name from the number

	if($incategory !~/^childforum-[0-9]+/){
        foreach (@forums) {
            ($trash, $tempcategoryname, $tempcategoryplace, $trash) = split(/\t/, $_);
            if ($incategory eq $tempcategoryplace && $tempcategoryname !~/childforum-[0-9]+/) {
                $category = $tempcategoryname;
                $categoryn = "在 '$tempcategoryname' 分类中增加新的论坛";
            }
        }
	}else{
        foreach (@forums) {
            ($tempforumno, $tempcategoryname, $tempcategoryplace, $tempforumname) = split(/\t/, $_);
            if ($incategory eq "childforum-$tempforumno") {
                $category = $incategory;
                $incategory = $tempcategoryplace;
                $categoryn = "在 '$tempforumname' 中增加新的子论坛";
		$modiii = "<BR><font color=blue>子论坛会自动继承父论坛的斑竹，所以注意不要重复输入斑竹</font>";
            }
        }
	}

    ($fgwidth,$fgwidth1) = split(/\|/,$fgwidth);
    ($fgheight,$fgheight1) = split(/\|/,$fgheight);

# Present the form to be filled in

        print qq~
        
        <tr>
        <td bgcolor=#EEEEEE align=center colspan=2>
        <font color=#990000><b>$categoryn</b>
        </td></tr>

        <form action="$thisprog" method="post" enctype="multipart/form-data" name=FORM>
        <input type=hidden name="categorynumber" value="$incategory">
        <input type=hidden name="categoryname" value="$category">
        <input type=hidden name="action" value="processnew">       
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛名称</b><br>请输入新论坛的名称<BR>(请控制在 20 个汉字内)</font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=40 name="forumname" value="$forumname" maxlength=40></td>
        </tr>       
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛描述</b><br>请输入新论坛的描述，支持 HTML 语法</font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=40 name="forumdescription" value="$forumdescription"></td>
        </tr>   
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛版主</b><br>请输入论坛版主，如果您希望有多个版主，请使用 "," (英文逗号，不是中文逗号)隔开。<BR><B>例如</B>：山鹰, 花无缺</font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=40 name="forummoderator" value="$forummoderator">$modiii</td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否使用 HTML 标签？</b></font></td>
        <td bgcolor=#FFFFFF>
        <select name="htmlstate">
        <option value="on">使用<option value="off" selected>不使用</select>
        </td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否使用 LeoBBS 标签？</b></font></td>
        <td bgcolor=#FFFFFF>
        <select name="idmbcodestate">
        <option value="on" selected>使用<option value="off">不使用</select>
        </td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否作为私有论坛？</b></font></td>
        <td bgcolor=#FFFFFF>
        <select name="privateforum">
        <option value="yes">是<option value="no" selected>否</select> 对坛主和总斑竹无效
        </td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>私有论坛密码</b>(只对私有论坛有效)</font></td>
        <td bgcolor=#FFFFFF>
       <input type=text size=12 name="forumpass" value="$forumpass" maxlength=20> 对坛主和总斑竹无效</td>
        </td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否隐藏论坛？</b></font></td>
        <td bgcolor=#FFFFFF>
        <select name="hiddenforum">
        <option value="yes">是<option value="no" selected>否</select>
        </td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否显示导航栏？</b></font></td>
        <td bgcolor=#FFFFFF>
        <select name="indexforum">
        <option value="yes" selected>是<option value="no" >否</select>
        </td>
        </tr>

        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛性质</b><br>1. 正规论坛-只允许注册会员发言<br>2. 开放论坛-允许所有人发言<br>3. 评论论坛-坛主和版主允许发言，其他注册用户只能回复<br>4. 精华区-只允许版主和坛主发言和操作<br>5. 认证论坛-除坛主和版主外，其他注册用户发言需要认证<br>6. 纯子论坛-里面只有子论坛，而父论坛不允许发贴回复<br></font></td>
        <td bgcolor=#FFFFFF>
        <select name="startnewthreads">
        <option value="yes" selected>正规论坛<option value="all">开放论坛<option value="follow">评论论坛<option value="no">精华区<option value="cert">认证论坛<option value="onlysub">纯子论坛</select>
        </td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛图片（支持FLASH）</b><br>请输入图片名称，此图必须在 myimages 目录下，被用来放置在论坛页面左上方，大小请控制在 160*60 以内。<BR><b>请不要包含 URL 地址或绝对路径！</b></font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=20 name="forumgraphic" value="logo.gif">
~;

opendir (DIR, "${imagesdir}myimages");
@thd = readdir(DIR);
closedir (DIR);
        my $myimages="";
        $topiccount = @thd;
        @thd=sort @thd;
        for (my $i=0;$i<$topiccount;$i++){
            next if (($thd[$i] eq ".")||($thd[$i] eq ".."));
            $myimages.=qq~<option value="$thd[$i]">$thd[$i]~;
        }
        $myimages =~ s/value=\"$action\"/value=\"$action\" selected/;        
print qq~
<script>
function select(){
document.FORM.forumgraphic.value=FORM.image.value;
document.bbsimg.src = "$imagesurl/myimages/"+FORM.image.value;}
function select2(){
document.FORM.teamlogo.value=FORM.image2.value;
document.bbsimg.src = "$imagesurl/myimages/"+FORM.image2.value;}
function select3(){
document.bbsimg.src = FORM.addme.value;}
</script>
<select name="image" onChange=select()><option value="blank.gif">选择图片$myimages</select></td>
        </tr>

        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛FLASH动画高度、宽度</b><br>请正确输入FLASH动画的高度及宽度。<BR></font></td>
        <td bgcolor=#FFFFFF>
        宽度：<input type=text size=3 name="fgwidth">　　高度：<input type=text size=3 name="fgwidth1"></td>
        </tr>
               
	<tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>队伍图片</b>(如果没有，请保持原样)<br>请输入图片名称，此图片被用来放置在首页面下。<BR><b>不要包含 URL 地址或绝对路径！</b></font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=20 name="teamlogo" value=""> <select name="image2" onChange=select2()><option value="blank.gif">选择图片$myimages</select></td>
        </tr> 
         
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>队伍图片FLASH动画高度、宽度</b><br>请正确输入FLASH动画的高度及宽度。<BR></font></td>
        <td bgcolor=#FFFFFF>
        宽度：<input type=text size=3 name="fgheight">　　高度：<input type=text size=3 name="fgheight1"></td>
        </tr>

	<tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>上传论坛/队伍图片</b><br>请输入图片名称，此图片被用作论坛图片/队伍图片。</font></td>
        <td bgcolor=#FFFFFF>
        <input type="file" size=20 name="addme" onchange="select3()"><br>支持类型：gif、jpg、bmp、png、swf</td>
        </tr> 

        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>队伍网址</b>(如果没有，请保持原样)<br>用来做上面论坛图片的地址链接</td>
        <td bgcolor=#FFFFFF>
        <input type=text size=40 name="teamurl" value="http://"></td>
        </tr><tr>
        <td bgcolor=#FFFFFF colspan=2>
<font color=#333333><b>图像预览(不支持 Flash)</b></font><br><IMG border=0 name=bbsimg src="$imagesurl/myimages/blank.gif" align="absmiddle" onload="javascript:if(this.width>document.body.clientWidth-333)this.width=document.body.clientWidth-333"></td>
        </tr>
        <tr>
        <td bgcolor=#FFFFFF align=center colspan=2>
        <input type=submit value="提 交"></form></td></tr></table></td></tr></table>
        ~;
        
} # end route   


##################################################################################
######## Subroutes ( Create Forum )


sub createforum {
#		&errorout("保密论坛，密码不能空！！") if (($new_privateforum eq "yes")&&($new_forumpass eq ""));
		&errorout("对不起，论坛名字过长，请控制在 20 个汉字内！") if (length($new_forumname) >40);
		&errorout("论坛名字不能空！！") if ($new_forumname eq "");
		&errorout("论坛描述不能空！！") if ($new_forumdescription eq "");
		$new_privateforum = "yes" if ($new_forumpass ne "");

&douppics();

                $filetoopen = "$lbdir" . "data/allforums.cgi";
	        &winlock($filetoopen) if ($OS_USED eq "Nt");
                open(FILE, "$filetoopen");
  	        flock(FILE, 1) if ($OS_USED eq "Unix");
                @forums = <FILE>;
                close(FILE);
	        &winunlock($filetoopen) if ($OS_USED eq "Nt");

                foreach (@forums) {
                    ($forumid, $binit) = split(/\t/,$_);
                    if ($forumid > $high) { $high = $forumid; }
                    }

                $high++;

                $newforumid = $high;

                $dirtomake = "$lbdir" . "forum$newforumid";
                mkdir ("$dirtomake", 0777);

                $dirtomake1 = "$lbdir" . "FileCount/$newforumid";
                mkdir ("$dirtomake1", 0777);

                $filetomake = "$dirtomake1/index.html";
                open(FILE,">$filetomake");
                print FILE "-";
                close(FILE);

                $dirtomake1 = "$imagesdir" . "$usrdir/$newforumid";
                mkdir ("$dirtomake1", 0777);

                $filetomake = "$dirtomake1/index.html";
                open(FILE,">$filetomake");
                print FILE "-";
                close(FILE);

                $filetomake = "$dirtomake/index.html";
                open(FILE,">$filetomake");
                print FILE "-";
                close(FILE);

                $filetomake = "$lbdir" . "boarddata/listno$newforumid.cgi";
                open(FILE,">$filetomake");
                close(FILE);
                $filetomake = "$lbdir" . "boarddata/listall$newforumid.cgi";
                open(FILE,">$filetomake");
                close(FILE);

	        open(FILE, ">${lbdir}boarddata/foruminfo$newforumid.cgi");
	        print FILE "%%%%%%\t0\t0\t\t\t\n";
                close(FILE);

                $filetomake = "$dirtomake/.htaccess";
                open(FILE, ">$filetomake");
                print FILE "AuthUserFile /dev/null\n";
                print FILE "AuthGroupFile /dev/null\n";
                print FILE "AuthName DenyViaWeb\n";
                print FILE "AuthType Basic\n";
                print FILE "\n\n\n\n";
                print FILE "<Limit GET>\n";
                print FILE "order allow,deny\n";
                print FILE "deny from all\n";
                print FILE "</Limit>\n";
                close (FILE);

my @molist = split(/\,/,$new_forummoderator);
foreach $_ (@molist){
    chomp $_;
    $_ =~ s/ /\_/g;
    $_ =~ tr/A-Z/a-z/;
    next if ($_ eq "");
    next if (($_ =~ /诚聘中/i)||($_ =~ /斑竹/i)||($_ =~ /全体管理人员/i)||($_ =~ /管理员/i)||($_ =~ /暂时空缺/i)||($_ =~ /版主/i)||($_ =~ /坛主/i));
    my $namenumber = &getnamenumber($_);
    &checkmemfile($_,$namenumber);
    if ((!(-e "${lbdir}$memdir/$namenumber/$_.cgi"))&&(!(-e "${lbdir}$memdir/old/$_.cgi"))) { &winunlock($filetoopen) if ($OS_USED eq "Nt"); &errorout("论坛版主名单中，$_ 这个用户 ID 是不存在的！");}
}

                $filetomake1 = "$dirtomake/foruminfo.cgi";
                open(FILE,">$filetomake1");
                print FILE "$newforumid\t$new_categoryname\t$new_categorynumber\t$new_forumname\t$new_forumdescription\t$new_forummoderator\t$new_htmlstate\t$new_idmbcodestate\t$new_privateforum\t$new_startnewthreads\t\t\t0\t0\t$new_forumgraphic\t$new_ratings\t$misc\t$new_forumpass\t$new_hiddenforum\t$new_indexforum\t$new_teamlogo\t$new_teamurl\t$new_fgwidth|$new_fgwidth1\t$new_fgheight|$new_fgheight1\t$new_miscad4\t$todayforumpost\t$new_miscad5\t";
                close(FILE);

                $filetoopen = "$lbdir" . "data/allforums.cgi";
#		&winlock($filetoopen) if ($OS_USED eq "Nt");
                open(FILE, "$filetoopen");
#	        flock(FILE, 1) if ($OS_USED eq "Unix");
                @forums = <FILE>;
                close(FILE);

                open(FILE, ">$filetoopen");
                flock(FILE, 2) if ($OS_USED eq "Unix");
                foreach $line (@forums) {
                    chomp $line;
                    ($tempforumno,undef,$tempcategorynumber)=split(/\t/,$line);
                    print FILE "$line\n";
                    if($new_categoryname =~/childforum-[0-9]+/){
                print FILE "$newforumid\t$new_categoryname\t$new_categorynumber\t$new_forumname\t$new_forumdescription\t$new_forummoderator\t$new_htmlstate\t$new_idmbcodestate\t$new_privateforum\t$new_startnewthreads\t\t\t0\t0\t$new_forumgraphic\t$new_ratings\t$misc\t$new_forumpass\t$new_hiddenforum\t$new_indexforum\t$new_teamlogo\t$new_teamurl\t$new_fgwidth|$new_fgwidth1\t$new_fgheight|$new_fgheight1\t$new_miscad4\t$todayforumpost\t$new_miscad5\t\n" if($new_categoryname eq "childforum-$tempforumno");
                $Get=1;
                    }
                    }
                print FILE "$newforumid\t$new_categoryname\t$new_categorynumber\t$new_forumname\t$new_forumdescription\t$new_forummoderator\t$new_htmlstate\t$new_idmbcodestate\t$new_privateforum\t$new_startnewthreads\t\t\t0\t0\t$new_forumgraphic\t$new_ratings\t$misc\t$new_forumpass\t$new_hiddenforum\t$new_indexforum\t$new_teamlogo\t$new_teamurl\t$new_fgwidth|$new_fgwidth1\t$new_fgheight|$new_fgheight1\t$new_miscad4\t$todayforumpost\t$new_miscad5\t\n" if($new_categoryname !~/childforum-[0-9]+/);
                close(FILE);
#	        &winunlock($filetoopen) if ($OS_USED eq "Nt");

	    open(FILE, ">${lbdir}boarddata/forumposts$newforumid.pl");
	    print FILE "\$threads = 0;\n\$posts = 0;\n\$todayforumpost = \"0\";\n1;\n";
            close(FILE);

                print qq~
                <tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF>
                <b>欢迎来到论坛管理中心 / 增加论坛结果</b>
                </td></tr>
                <tr>
                <td bgcolor=#FFFFFF colspan=2>
                <font color=#333333>
                ~;

                print "<b>详细资料</b><p>\n";
                print "<ul>\n";
                if (-e $dirtomake) {
                print "<li><b>新论坛目录已经建立</b><p>\n";
                    }
                    else {
                        print "<li><b>新论坛目录没有建立</b><p>请查看是否改变了目录属性？请改属性回 777 ！<p>\n";
                        }


                $filetoopen = "$dirtomake/index.html";
                if (-e $filetoopen) {
                    print "<li><b>新论坛 (index.html) 文件建立</b><p>\n";
                    }
                    else {
                        print "<li><b>新论坛 (index.html) 文件没有建立</b><p>请查看是否改变了目录属性？请改属性回 777 ！\n";
                        }
                print "$filetoopen<p>\n";
                print "</ul>\n";
&forumjump;
print "</td></tr></table></td></tr></table>";
} ######## end routine

sub warning {
    print qq~<tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF><b>欢迎来到论坛管理中心 / 删除论坛</b></td></tr>
<tr><td bgcolor=#EEEEEE align=center colspan=2><font color=#990000><b>警告！！</b></td></tr>
<tr><td bgcolor=#FFFFFF align=center colspan=2><font color=#333333>如果您确定要删除论坛，那么请点击下面链接<p>
>> <a href="$thisprog?action=delete&checkaction=yes&forum=$inforum">删除论坛以及论坛下的所有文件</a> <<
</td></tr></table></td></tr></table>
~;
}

sub deleteforum { #start
    my $thistime=time;
    open(FILE, ">>${lbdir}data/baddel.cgi");
    print FILE "$inmembername\t密码不显示\t$ENV{'REMOTE_ADDR'}\t$ENV{'HTTP_X_FORWARDED_FOR'}/$ENV{'HTTP_CLIENT_IP'}\t删除论坛$forumname\t$thistime\t\n";
    close(FILE);
    undef $thistime;

    opendir (DIRS, "${imagesdir}$usrdir/$inforum");
    my @files = readdir(DIRS);
    closedir (DIRS);
    foreach (@files) {
    	chomp $_;
	unlink ("${imagesdir}$usrdir/$inforum/$_");
    }
    unlink ("${imagesdir}$usrdir/$inforum/.htaccess");
    rmdir ("${imagesdir}$usrdir/$inforum");

    opendir (DIRS, "${lbdir}forum$inforum");
    my @files = readdir(DIRS);
    closedir (DIRS);
    foreach (@files) {
    	chomp $_;
	unlink ("${lbdir}forum$inforum/$_");
    }
    unlink ("${lbdir}forum$inforum/.htaccess");
    rmdir ("${lbdir}forum$inforum");

    opendir (DIRS, "${lbdir}FileCount/$inforum");
    my @files = readdir(DIRS);
    closedir (DIRS);
    foreach (@files) {
    	chomp $_;
	unlink ("${lbdir}FileCount/$inforum/$_");
    }
    unlink ("${lbdir}FileCount/$inforum/.htaccess");
    rmdir ("${lbdir}FileCount/$inforum");

    unlink ("${lbdir}data/news$inforum.cgi");
    unlink ("${lbdir}data/style$inforum.cgi");
    unlink ("${lbdir}boarddata/list$inforum.cgi");
    unlink ("${lbdir}boarddata/listno$inforum.cgi");
    unlink ("${lbdir}boarddata/listall$inforum.cgi");
    unlink ("${lbdir}boarddata/xzb$inforum.cgi");
    unlink ("${lbdir}boarddata/xzbs$inforum.cgi");
    unlink ("${lbdir}boarddata/lastnum$inforum.cgi");
    unlink ("${lbdir}boarddata/ontop$inforum.cgi");
    unlink ("${lbdir}boarddata/jinghua$inforum.cgi");
    unlink ("${lbdir}boarddata/recyclebin$inforum.cgi");
    unlink ("${lbdir}boarddata/adminlog$inforum.cgi");

		    opendir (DIRS, "${lbdir}$saledir");
		    my @files = readdir(DIRS);
		    closedir (DIRS);

		    my @files = grep(/^$inforum\_/i, @files);
		    foreach (@files) {
		        chomp $_;
		        unlink ("${lbdir}$saledir/$_");
    		    }


    $filetoopen = "$lbdir" . "data/allforums.cgi";
    &winlock($filetoopen) if ($OS_USED eq "Nt");
    open(FILE,"$filetoopen");
    flock(FILE, 1) if ($OS_USED eq "Unix");
    my @forums = <FILE>;
    close(FILE);

    open(FILE,">$filetoopen");
    flock(FILE,2) if ($OS_USED eq "Unix");
    foreach (@forums) {
        chomp $_;
	my ($forumid, $category, $categoryplace, $forumname, $forumdescription, $forummoderator ,$htmlstate ,$idmbcodestate ,$privateforum, $startnewthreads ,$lastposter ,$lastposttime, $threads, $posts, $forumgraphic, $miscad2, $misc,$forumpass,$hiddenforum,$indexforum,$teamlogo,$teamurl, $fgwidth, $fgheight, $miscad4, $todayforumpost, $miscad5) = split(/\t/,$_);
    	next if ($forumid !~ /^[0-9]+$/);
	if ($forumid ne $inforum) {
            print FILE "$_\n";
        }
    }
    close(FILE);
    &winunlock($filetoopen) if ($OS_USED eq "Nt");

    open(FILE, "${lbdir}boarddata/foruminfo$inforum.cgi");
    ($no, $thdcount, $threadcount, $no) = split(/\t/,<FILE>);
    close(FILE);

    $threadcount = 0 if ($threadcount eq "");
    $thdcount    = 0 if ($thdcount eq "");

    require "$lbdir" . "data/boardstats.cgi";
    $totalthreads = $totalthreads - $thdcount;
    $totalposts   = $totalposts   - $threadcount;

    $filetomake = "$lbdir" . "data/boardstats.cgi";
    &winlock($filetomake) if ($OS_USED eq "Nt");
    open(FILE, ">$filetomake");
    flock(FILE, 2) if ($OS_USED eq "Unix");
    print FILE "\$lastregisteredmember = \'$lastregisteredmember\'\;\n";
    print FILE "\$totalmembers = \'$totalmembers\'\;\n";
    print FILE "\$totalthreads = \'$totalthreads\'\;\n";
    print FILE "\$totalposts = \'$totalposts\'\;\n";
    print FILE "\n1\;";
    close (FILE);
    &winunlock($filetomake) if ($OS_USED eq "Nt");

    unlink ("${lbdir}boarddata/forumposts$inforum.pl");
    unlink ("${lbdir}boarddata/foruminfo$inforum.cgi");

    print qq~<tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF><b>欢迎来到论坛管理中心 / 删除论坛结果</b></td></tr>
<tr><td bgcolor=#FFFFFF colspan=2><font color=#990000>
<center><b>论坛已被删除</b></center><p>
共有 $thdcount 主题被删除<p>
共有 $threadcount 回复被删除<p>
</td></tr></table></td></tr></table>
~;
&forumjump;
}

sub editform {

         $filetoopen = "$lbdir" . "data/allforums.cgi";
         open(FILE,"$filetoopen");
         @forums = <FILE>;
         close(FILE);

         foreach $forum (@forums) {
            chomp $forum;
	    next if ($forum eq "");
            ($forumid,$notneeded,$notneeded,$gforumname) = split(/\t/,$forum);
    	    next if ($forumid !~ /^[0-9]+$/);
                if ($forumid eq "$inforum") {
                    ($forumid, $category, $categoryplace, $forumname, $forumdescription, $forummoderator ,$htmlstate ,$idmbcodestate ,$privateforum, $startnewthreads ,$lastposter ,$lastposttime, $threads, $posts, $forumgraphic, $miscad2, $misc,$forumpass,$hiddenforum,$indexforum,$teamlogo,$teamurl, $fgwidth, $fgheight, $miscad4, $todayforumpost, $miscad5) = split(/\t/,$forum);
                }
            $forumname[$forumid]="$gforumname";
         }
		if($category=~/childforum-[0-9]+/){
			$category=~s/^childforum-//;
			$categoryn="编辑 '$forumname[$category]' 中的子论坛 '$forumname' ";
			$modiii = "<BR><font color=blue>子论坛会自动继承父论坛的斑竹，所以注意不要重复输入斑竹</font>";
		}else{
			$categoryn="编辑 '$category' 分类中的 '$forumname' 论坛";
			$modiii = "";
		}
    ($fgwidth,$fgwidth1) = split(/\|/,$fgwidth);
    ($fgheight,$fgheight1) = split(/\|/,$fgheight);
    
# Present the form to be filled in


        print qq~
        <tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF>
        <b>欢迎来到论坛管理中心 / 编辑论坛</b>
        </td></tr>
        <tr>
        <td bgcolor=#EEEEEE align=center colspan=2>
        <font color=#990000><b>$categoryn</b>
        </td></tr>

        <form action="$thisprog" method="post" enctype="multipart/form-data" name=FORM>
        <input type=hidden name="action" value="doedit">
        <input type=hidden name="forum" value="$inforum">
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛名称</b><br>请输入论坛名称</font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=40 name="forumname" value="$forumname"></td>
        </tr>       
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛描述</b><br>请输入论坛描述，支持 HTML 语法</font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=40 name="forumdescription" value="$forumdescription"></td>
        </tr>   
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛版主</b><br>请输入论坛版主，如果您希望有多个版主，请使用 "," (英文逗号，不是中文逗号)隔开。<BR><B>例如</B>：山鹰, 花无缺</font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=40 name="forummoderator" value="$forummoderator">$modiii</td>
        </tr>
        ~;
        
        $tempoutput = qq~<select name="htmlstate"><option value="on">使用<option value="off">不使用</select>~;
        $tempoutput =~ s/value=\"$htmlstate\"/value=\"$htmlstate\" selected/g;
        
        print qq~
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否使用 HTML 标签？</b></font></td>
        <td bgcolor=#FFFFFF>
        $tempoutput
        </td>
        </tr>
        ~;
        
        $tempoutput = qq~<select name="idmbcodestate"><option value="on">使用<option value="off">不使用</select>~;
        $tempoutput =~ s/value=\"$idmbcodestate\"/value=\"$idmbcodestate\" selected/g;
        
        print qq~
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否使用 LeoBBS 标签？</b></font></td>
        <td bgcolor=#FFFFFF>
        $tempoutput
        </td>
        </tr>
        ~;
        
        $tempoutput = qq~<select name="privateforum"><option value="yes">是<option value="no">否</select>~;
        $tempoutput =~ s/value=\"$privateforum\"/value=\"$privateforum\" selected/g;
        if (!$privateforum) { 
            $tempoutput = qq~<select name="privateforum"><option value="yes">是<option value="no" selected>否</select>~;
            }
        print qq~
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否作为私有论坛？</b></font></td>
        <td bgcolor=#FFFFFF>
        $tempoutput  对坛主和总斑竹无效
        </td>
        </tr>
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>私有论坛密码</b>(只对私有论坛有效)</font></td>
        <td bgcolor=#FFFFFF>
       <input type=text size=12 name="forumpass" value="$forumpass" maxlength=20> 对坛主和总斑竹无效</td>
        </td>
        </tr>
        ~;
        
        $tempoutput = qq~<select name="hiddenforum"><option value="yes">是<option value="no">否</select>~;
        $tempoutput =~ s/value=\"$hiddenforum\"/value=\"$hiddenforum\" selected/g;
        if (!$hiddenforum) { 
            $tempoutput = qq~<select name="hiddenforum"><option value="yes">是<option value="no" selected>否</select>~;
            }
        print qq~
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否隐藏论坛？</b></font></td>
        <td bgcolor=#FFFFFF>
        $tempoutput
        </td>
        </tr>
        ~;
        
        $tempoutput = qq~<select name="indexforum"><option value="yes">是<option value="no">否</select>~;
        $tempoutput =~ s/value=\"$indexforum\"/value=\"$indexforum\" selected/g;
        if (!$indexforum) { 
            $tempoutput = qq~<select name="indexforum"><option value="yes" selected>是<option value="no" >否</select>~;
            }
        print qq~
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否显示导航栏？</b></font></td>
        <td bgcolor=#FFFFFF>
        $tempoutput
        </td>
        </tr>
        
        ~;
        
        $tempoutput = qq~<select name="startnewthreads"><option value="yes" selected>正规论坛<option value="all">开放论坛<option value="follow">评论论坛<option value="no">精华区<option value="cert">认证论坛<option value="onlysub">纯子论坛</select>~;
        $tempoutput =~ s/value=\"$startnewthreads\"/value=\"$startnewthreads\" selected/g;
        
        print qq~
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛性质</b><br>1. 正规论坛-只允许注册会员发言<br>2. 开放论坛-允许所有人发言<br>3. 评论论坛-坛主和版主允许发言，其他注册用户只能回复<br>4. 精华区-只允许版主和坛主发言和操作<br>5. 认证论坛-除坛主和版主外，其他注册用户发言需要认证<br>6. 纯子论坛-里面只有子论坛，而父论坛不允许发贴回复<br></font></td>
        <td bgcolor=#FFFFFF>
        $tempoutput
        </td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛图片</b><br>请输入图片名称，此图必须在 myimages 目录下，被用来放置在论坛页面左上方，大小请控制在 160*60 以内。<BR><b>请不要包含 URL 地址或绝对路径！</b></font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=30 name="forumgraphic" value="$forumgraphic"> 
~;
opendir (DIR, "${imagesdir}myimages");
@thd = readdir(DIR);
closedir (DIR);
        my $myimages="";
        $topiccount = @thd;
        @thd=sort @thd;
        for (my $i=0;$i<$topiccount;$i++){
            next if (($thd[$i] eq ".")||($thd[$i] eq ".."));
            $myimages.=qq~<option value="$thd[$i]">$thd[$i]~;
        }
        $myimages =~ s/value=\"$action\"/value=\"$action\" selected/;        
print qq~
<script>
function select(){
document.FORM.forumgraphic.value=FORM.image.value;
document.bbsimg.src = "$imagesurl/myimages/"+FORM.image.value;}
function select2(){
document.FORM.teamlogo.value=FORM.image2.value;
document.bbsimg.src = "$imagesurl/myimages/"+FORM.image2.value;}
function select3(){
document.bbsimg.src = FORM.addme.value;}
</script>
<select name="image" onChange=select()><option value="blank.gif">选择图片$myimages</select></td>
        </tr>
	<tr>
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛FLASH动画高度、宽度</b><br>请正确输入 FLASH 动画的高度及宽度。<BR></font></td>
        <td bgcolor=#FFFFFF>
        宽度：<input type=text size=3 name="fgwidth" value="$fgwidth">　　高度：<input type=text size=3 name="fgwidth1" value="$fgwidth1"></td>
        </tr>
	<tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>队伍图片</b>(如果没有，请保持原样)<br>请输入图片名称，此图必须在 myimages 目录下，被用来放置在主页面下。<BR><b>不要包含 URL 地址或绝对路径！</b></font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=30 name="teamlogo" value="$teamlogo"> <select name="image2" onChange=select2()><option value="blank.gif">选择图片$myimages</select></td>
        </tr> 
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>队伍图片FLASH动画高度、宽度</b><br>请正确输入 FLASH 动画的高度及宽度。<BR></font></td>
        <td bgcolor=#FFFFFF>
        宽度：<input type=text size=3 name="fgheight" value="$fgheight">　　高度：<input type=text size=3 name="fgheight1" value="$fgheight1"></td>
        </tr>
	<tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>上传论坛/队伍图片</b><br>请输入图片名称，此图片被用作论坛图片/队伍图片。</font></td>
        <td bgcolor=#FFFFFF>
        <input type="file" size=20 name="addme" onchange="select3()"><br>支持类型：gif、jpg、bmp、png、swf</td>
        </tr> 
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>队伍网址</b>(如果没有，请保持原样)</td>
        <td bgcolor=#FFFFFF>
        <input type=text size=40 name="teamurl" value="$teamurl"></td>
        </tr><tr>
        <td bgcolor=#FFFFFF colspan=2>
<font color=#333333><b>图像预览(不支持 Flash)</b></font><br><IMG border=0 name=bbsimg src="$imagesurl/myimages/blank.gif" align="absmiddle"></td>
        </tr>
        <tr>
        <td bgcolor=#F0F0F0 align=center colspan=2>
        <input type=submit value="提 交"></form></td></tr></table><center>
        ~;
        print "</td></tr></table>";
} # end route   

##################################################################################
######## Subroutes ( Processing the edit of a forum)


sub doedit {
#	&errorout("保密论坛，密码不能空！！") if (($new_privateforum eq "yes")&&($new_forumpass eq ""));
	&errorout("对不起，论坛名字过长，请控制在 20 个汉字内！") if (length($new_forumname) >40);
	&errorout("论坛名字不能空！！") if ($new_forumname eq "");
	&errorout("论坛描述不能空！！") if ($new_forumdescription eq "");
	$new_privateforum = "yes" if ($new_forumpass ne "");

         $filetoopen = "$lbdir" . "data/allforums.cgi";
#         &winlock($filetoopen) if ($OS_USED eq "Nt");
	 open(FILE,"$filetoopen");
#         flock(FILE, 1) if ($OS_USED eq "Unix");
         @forums = <FILE>;
         close(FILE);

         foreach $forum (@forums) {
             chomp $forum;
 	     next if ($forum eq "");
             ($forumid, $notneeded) = split(/\t/,$forum);
    	     next if ($forumid !~ /^[0-9]+$/);
             if ($forumid eq $inforum) {
                 ($forumid, $category, $categoryplace, $forumname, $forumdescription, $forummoderator ,$htmlstate ,$idmbcodestate ,$privateforum, $startnewthreads ,$lastposter ,$lastposttime, $threads, $posts, $forumgraphic, $miscad2, $misc, $forumpass,$hiddenforum,$indexforum,$teamlogo,$teamurl, $fgwidth, $fgheight, $miscad4, $todayforumpost, $miscad5) = split(/\t/,$forum);
             }
        }

                $editedline = "$inforum\t$category\t$categoryplace\t$new_forumname\t$new_forumdescription\t$new_forummoderator\t$new_htmlstate\t$new_idmbcodestate\t$new_privateforum\t$new_startnewthreads\t$lastposter\t$lastposttime\t$threads\t$posts\t$new_forumgraphic\t$new_ratings\t$misc\t$new_forumpass\t$new_hiddenforum\t$new_indexforum\t$new_teamlogo\t$new_teamurl\t$new_fgwidth|$new_fgwidth1\t$new_fgheight|$new_fgheight1\t$new_miscad4\t$todayforumpost\t$new_miscad5\t";
                chomp $editedline;


	&douppics();
	
                mkdir ("${lbdir}FileCount/$newforumid", 0777);
                mkdir ("${imagesdir}$usrdir/$newforumid", 0777);

my @molist = split(/\,/,$new_forummoderator);
foreach $_ (@molist){
    chomp $_;
    $_ =~ s/ /\_/g;
    $_ =~ tr/A-Z/a-z/;
    next if ($_ eq "");
    next if (($_ =~ /诚聘中/i)||($_ =~ /斑竹/i)||($_ =~ /全体管理人员/i)||($_ =~ /管理员/i)||($_ =~ /暂时空缺/i)||($_ =~ /版主/i)||($_ =~ /坛主/i));
    my $namenumber = &getnamenumber($_);
    &checkmemfile($_,$namenumber);
    if ((!(-e "${lbdir}$memdir/$namenumber/$_.cgi"))&&(!(-e "${lbdir}$memdir/old/$_.cgi"))) { 
#    	&winunlock($filetoopen) if ($OS_USED eq "Nt");
    	&errorout("论坛版主名单中，$_ 这个用户 ID 是不存在的！");
    }
}

                $dirtomake = "$lbdir" . "forum$inforum";
                $filetomake1 = "$dirtomake/foruminfo.cgi";
                open(FILE,">$filetomake1");
                print FILE $editedline;
                close(FILE);

                # Lets re-open the file

                $filetoopen = "$lbdir" . "data/allforums.cgi";
                open(FILE,"$filetoopen");
#                flock(FILE, 1) if ($OS_USED eq "Unix");
                @forums = <FILE>;
                close(FILE);

                # Lets remake the file...

                open(FILE,">$filetoopen");
                flock(FILE,2) if ($OS_USED eq "Unix");
                open(FILEBAK, ">$filetoopen.pl");

				foreach $forum (@forums) {
                chomp $forum;
                ($tempforumid,$notneeded) = split(/\t/,$forum);
                    if ($tempforumid eq "$inforum") {
                        print FILE "$editedline\n";
                        print FILEBAK "$editedline\n";
						}
                        else {
                            print FILE "$forum\n";
							print FILEBAK "$forum\n";
                            }
                    }
                close(FILEBAK);
				close (FILE);
#	            &winunlock($filetoopen) if ($OS_USED eq "Nt");


                 print qq~
                <tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF>
                <b>欢迎来到论坛管理中心 / 编辑论坛结果</b>
                </td></tr>
                <tr>
                <td bgcolor=#EEEEEE align=center colspan=2>
                <font color=#333333><b>所有信息已经保存</b><p>
                如果您设定了某人为版主，你或许会想从管理中心编辑他的资料，使他成为版主。<BR>
                其实这个是没必要的。这个仅仅影响发贴后名字边上的 '斑竹' 图标，非版主不显示 <br>
				'斑竹' 图标，并且不在管理团队中显示！但是两种斑竹权力是一样的。</font>
                </td></tr></table><center>
                ~;
print "</td></tr></table>";
&forumjump;

            } # end routine

##################################################################################
######## Subroutes ( Add category/forum Form )


sub catform {

# Present the form to be filled in
        print qq~
        <form action="$thisprog" method="post" enctype="multipart/form-data" name=FORM>
        <input type=hidden name="action" value="doaddcategory">
        <input type=hidden name="category" value="$incategory">
        <tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF>
        <b>欢迎来到论坛管理中心 / 增加分类(同时增加一个论坛)</b>
        </td></tr>
        <tr>
        
        <tr>
        <td bgcolor=#EEEEEE align=center colspan=2>
        <font color=#990000><b>增加分类(同时增加一个论坛)</b>
        </td></tr>


        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>分类名称</b><br>请输入新分类名称</font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=40 name="categoryname" value="$categoryname"></td>
        </tr>

	<tr>
	<td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>区版主</b><br>请输入管理此分类的区版主，如果您希望有多个区版主，请使用 "," (英文逗号，不是中文逗号)隔开。<BR><B>例如</B>：山鹰, 花无缺</font></td> 
        <td bgcolor=#FFFFFF> 
        <input type=text size=40 name="catemods" value="$catemods"></td> 
        </tr>

        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛名称</b><br>请输入新论坛的名称<BR>(请控制在 20 个汉字内)</font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=40 name="forumname" value="$forumname" maxlength=40></td>
        </tr>       
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛描述</b><br>请输入新论坛的描述，支持 HTML 语法</font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=40 name="forumdescription" value="$forumdescription"></td>
        </tr>   
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛版主</b><br>请输入论坛版主，如果您希望有多个版主，请使用 "," (英文逗号，不是中文逗号)隔开。<BR><B>例如</B>：山鹰, 花无缺</font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=40 name="forummoderator" value="$forummoderator"></td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否使用 HTML 标签？</b></font></td>
        <td bgcolor=#FFFFFF>
        <select name="htmlstate">
        <option value="on">使用<option value="off" selected>不使用</select>
        </td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否使用 LeoBBS 标签？</b></font></td>
        <td bgcolor=#FFFFFF>
        <select name="idmbcodestate">
        <option value="on" selected>使用<option value="off">不使用</select>
        </td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否作为私有论坛？</b></font></td>
        <td bgcolor=#FFFFFF>
        <select name="privateforum">
        <option value="yes">是<option value="no" selected>否</select> 对坛主和总斑竹无效
        </td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>私有论坛密码</b>(只对私有论坛有效)</font></td>
        <td bgcolor=#FFFFFF>
       <input type=text size=12 name="forumpass" value="$forumpass" maxlength=20> 对坛主和总斑竹无效</td>
        </td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否隐藏论坛？</b></font></td>
        <td bgcolor=#FFFFFF>
        <select name="hiddenforum">
        <option value="yes">是<option value="no" selected>否</select>
        </td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>是否显示导航栏？</b></font></td>
        <td bgcolor=#FFFFFF>
        <select name="indexforum">
        <option value="yes" selected>是<option value="no" >否</select>
        </td>
        </tr>

        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛性质</b><br>1. 正规论坛-只允许注册会员发言<br>2. 开放论坛-允许所有人发言<br>3. 评论论坛-坛主和版主允许发言，其他注册用户只能回复<br>4. 精华区-只允许版主和坛主发言和操作<br>5. 认证论坛-除坛主和版主外，其他注册用户发言需要认证<br>6. 纯子论坛-里面只有子论坛，而父论坛不允许发贴回复<br></font></td>
        <td bgcolor=#FFFFFF>
        <select name="startnewthreads">
        <option value="yes" selected>正规论坛<option value="all">开放论坛<option value="follow">评论论坛<option value="no">精华区<option value="cert">认证论坛<option value="onlysub">纯子论坛</select>
        </td>
        </tr>
        
        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛图片（支持FLASH）</b><br>请输入图片名称，此图必须在 myimages 目录下，被用来放置在论坛页面左上方，大小请控制在 160*60 以内。<BR><b>请不要包含 URL 地址或绝对路径！</b></font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=20 name="forumgraphic" value="logo.gif">
~;

opendir (DIR, "${imagesdir}myimages");
@thd = readdir(DIR);
closedir (DIR);
        my $myimages="";
        $topiccount = @thd;
        @thd=sort @thd;
        for (my $i=0;$i<$topiccount;$i++){
            next if (($thd[$i] eq ".")||($thd[$i] eq ".."));
            $myimages.=qq~<option value="$thd[$i]">$thd[$i]~;
        }
        $myimages =~ s/value=\"$action\"/value=\"$action\" selected/;        
print qq~
<script>
function select(){
document.FORM.forumgraphic.value=FORM.image.value;
document.bbsimg.src = "$imagesurl/myimages/"+FORM.image.value;}
function select2(){
document.FORM.teamlogo.value=FORM.image2.value;
document.bbsimg.src = "$imagesurl/myimages/"+FORM.image2.value;}
function select3(){
document.bbsimg.src = FORM.addme.value;}
</script>
<select name="image" onChange=select()><option value="blank.gif">选择图片$myimages</select></td>
        </tr>

        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>论坛FLASH动画高度、宽度</b><br>请正确输入FLASH动画的高度及宽度。<BR></font></td>
        <td bgcolor=#FFFFFF>
        宽度：<input type=text size=3 name="fgwidth">　　高度：<input type=text size=3 name="fgwidth1"></td>
        </tr>
               
	<tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>队伍图片</b>(如果没有，请保持原样)<br>请输入图片名称，此图片被用来放置在首页面下。<BR><b>不要包含 URL 地址或绝对路径！</b></font></td>
        <td bgcolor=#FFFFFF>
        <input type=text size=20 name="teamlogo" value=""> <select name="image2" onChange=select2()><option value="blank.gif">选择图片$myimages</select></td>
        </tr> 

        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>队伍图片FLASH动画高度、宽度</b><br>请正确输入FLASH动画的高度及宽度。<BR></font></td>
        <td bgcolor=#FFFFFF>
        宽度：<input type=text size=3 name="fgheight">　　高度：<input type=text size=3 name="fgheight1"></td>
        </tr>
         
	<tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>上传论坛/队伍图片</b><br>请输入图片名称，此图片被用作论坛图片/队伍图片。</font></td>
        <td bgcolor=#FFFFFF>
        <input type="file" size=20 name="addme" onchange="select3()"><br>支持类型：gif、jpg、bmp、png、swf</td>
        </tr> 

        <tr>
        <td bgcolor=#FFFFFF width=40%>
        <font color=#333333><b>队伍网址</b>(如果没有，请保持原样)<br>用来做上面论坛图片的地址链接</td>
        <td bgcolor=#FFFFFF>
        <input type=text size=40 name="teamurl" value="http://"></td>
        </tr> 
        <td bgcolor=#FFFFFF colspan=2>
<font color=#333333><b>图像预览(不支持 Flash)</b></font><br><IMG border=0 name=bbsimg src="$imagesurl/myimages/blank.gif" align="absmiddle" onload="javascript:if(this.width>document.body.clientWidth-333)this.width=document.body.clientWidth-333"></td>
        </tr>
        <tr>
        <td bgcolor=#FFFFFF align=center colspan=2>
        <input type=submit value="提 交"></form></td></tr></table></td></tr></table>
        ~;
        
} # end route   


##################################################################################
######## Subroutes ( Create New cat/forum )


sub doaddcategory {
#		&errorout("保密论坛，密码不能空！！") if (($new_privateforum eq "yes")&&($new_forumpass eq ""));
		&errorout("对不起，论坛名字过长，请控制在 20 个汉字内！") if (length($new_forumname) >40);
		&errorout("论坛名字不能空！！") if ($new_forumname eq "");
		&errorout("论坛描述不能空！！") if ($new_forumdescription eq "");
		&errorout("论坛类别不能空！！") if ($new_categoryname eq "");

	&douppics();
	
               my @catemolist = split(/\,/,$new_catemods); 
               foreach(@catemolist){ 
               chomp $_; 
               $_ =~ s/ /\_/g; 
               $_ =~ tr/A-Z/a-z/; 
               next if ($_ eq ""); 
               my $namenumber = &getnamenumber($_);
		&checkmemfile($_,$namenumber);
               if ((!(-e "${lbdir}$memdir/$namenumber/$_.cgi"))&&(!(-e "${lbdir}$memdir/old/$_.cgi"))) {&errorout("区版主名单中，$_ 这个用户 ID 是不存在的！"); } 
               }

                $filetoopen = "$lbdir" . "data/allforums.cgi";
                open(FILE, "$filetoopen");
                @forums = <FILE>;
                close(FILE);

                foreach (@forums) {
                    ($forumid, $binit) = split(/\t/,$_);
                    if ($forumid > $high) { $high = $forumid; }
                    }

                $high++;

                $newforumid = $high;

                $dirtomake = "$lbdir" . "forum$newforumid";
                mkdir ("$dirtomake", 0777);

                $dirtomake1 = "$lbdir" . "FileCount/$newforumid";
                mkdir ("$dirtomake1", 0777);

                $filetomake = "$dirtomake1/index.html";
                open(FILE,">$filetomake");
                print FILE "-";
                close(FILE);

                $dirtomake1 = "$imagesdir" . "$usrdir/$newforumid";
                mkdir ("$dirtomake1", 0777);

                $filetomake = "$dirtomake1/index.html";
                open(FILE,">$filetomake");
                print FILE "-";
                close(FILE);

                $filetomake = "$dirtomake/index.html";
                open(FILE,">$filetomake");
                print FILE "-";
                close(FILE);

                $filetomake = "$lbdir" . "boarddata/listno$newforumid.cgi";
                open(FILE,">$filetomake");
                close(FILE);
                $filetomake = "$lbdir" . "boarddata/listall$newforumid.cgi";
                open(FILE,">$filetomake");
                close(FILE);

	        open(FILE, ">${lbdir}boarddata/foruminfo$newforumid.cgi");
	        print FILE "%%%%%%\t0\t0\t\t\t\n";
                close(FILE);

                $filetomake = "$dirtomake/.htaccess";
                open(FILE, ">$filetomake");
                print FILE "AuthUserFile /dev/null\n";
                print FILE "AuthGroupFile /dev/null\n";
                print FILE "AuthName DenyViaWeb\n";
                print FILE "AuthType Basic\n";
                print FILE "\n\n\n\n";
                print FILE "<Limit GET>\n";
                print FILE "order allow,deny\n";
                print FILE "deny from all\n";
                print FILE "</Limit>\n";
                close (FILE);

my @molist = split(/\,/,$new_forummoderator);
foreach $_ (@molist){
    chomp $_;
    $_ =~ s/ /\_/g;
    $_ =~ tr/A-Z/a-z/;
    next if ($_ eq "");
    next if (($_ =~ /诚聘中/i)||($_ =~ /斑竹/i)||($_ =~ /全体管理人员/i)||($_ =~ /管理员/i)||($_ =~ /暂时空缺/i)||($_ =~ /版主/i)||($_ =~ /坛主/i));
    my $namenumber = &getnamenumber($_);
    &checkmemfile($_,$namenumber);
    if ((!(-e "${lbdir}$memdir/$namenumber/$_.cgi"))&&(!(-e "${lbdir}$memdir/old/$_.cgi"))) { &winunlock($filetoopen) if ($OS_USED eq "Nt"); &errorout("论坛版主名单中，$_ 这个用户 ID 是不存在的！"); }
}

                $filetomake1 = "$dirtomake/foruminfo.cgi";
                open(FILE,">$filetomake1");
                print FILE "$newforumid\t$new_categoryname\t$incategory\t$new_forumname\t$new_forumdescription\t$new_forummoderator\t$new_htmlstate\t$new_idmbcodestate\t$new_privateforum\t$new_startnewthreads\t\t\t0\t0\t$new_forumgraphic\t$new_ratings\t$misc\t$new_forumpass\t$new_hiddenforum\t$new_indexforum\t$new_teamlogo\t$new_teamurl\t$new_fgwidth|$new_fgwidth1\t$new_fgheight|$new_fgheight1\t$new_miscad4\t$todayforumpost\t$new_miscad5\t";
                close(FILE);

                $filetoopen = "$lbdir" . "data/allforums.cgi";
#	        &winlock($filetoopen) if ($OS_USED eq "Nt");
                open(FILE, "$filetoopen");
#                flock(FILE, 1) if ($OS_USED eq "Unix");
                @forums = <FILE>;
                close(FILE);

                open(FILE, ">$filetoopen");
#               flock(FILE, 2) if ($OS_USED eq "Unix");
                foreach $line (@forums) {
                    chomp $line;
                    print FILE "$line\n";
                    }
                print FILE "$newforumid\t$new_categoryname\t$incategory\t$new_forumname\t$new_forumdescription\t$new_forummoderator\t$new_htmlstate\t$new_idmbcodestate\t$new_privateforum\t$new_startnewthreads\t\t\t0\t0\t$new_forumgraphic\t$new_ratings\t$misc\t$new_forumpass\t$new_hiddenforum\t$new_indexforum\t$new_teamlogo\t$new_teamurl\t$new_fgwidth|$new_fgwidth1\t$new_fgheight|$new_fgheight1\t$new_miscad4\t$todayforumpost\t$new_miscad5\t";
                close(FILE);
#	        &winunlock($filetoopen) if ($OS_USED eq "Nt");

               $catefiletoopen = "$lbdir" . "boarddata/catemod$incategory.cgi"; 
               open(CATEFILE,">$catefiletoopen"); 
               print CATEFILE "$new_catemods\n"; 
               close(CATEFILE);

	    open(FILE, ">${lbdir}boarddata/forumposts$newforumid.pl");
	    print FILE "\$threads = 0;\n\$posts = 0;\n\$todayforumpost = \"0\";\n1;\n";
            close(FILE);

                print qq~
                <tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF>
                <b>欢迎来到论坛管理中心 / 增加分类(同时增加一个论坛)结果</b>
                </td></tr>
                <tr>
                <td bgcolor=#FFFFFF colspan=2>
                <font color=#333333>
                ~;

                print "<b>详细信息：</b><p>\n";
                print "<ul>\n";
                if (-e $dirtomake) {
                print "<li><b>新的分类和论坛已经建立</b><p>\n";
                    }
                    else {
                        print "<li><b>新的分类和论坛没有建立</b><p>请查看是否改变了目录属性？请改属性回 777 ！<p>\n";
                        }


                $filetoopen = "$dirtomake/index.html";
                if (-e $filetoopen) {
                    print "<li><b>新论坛 (index.html) 文件建立</b><p>\n";
                    }
                    else {
                        print "<li><b>新论坛 (index.html) 文件没有建立</b><p>请查看是否改变了目录属性？请改属性回 777 ！<p>\n";
                        }
                print "$filetoopen<p>\n";
                print "</ul>\n";

print "</td></tr></table></td></tr></table>";
&forumjump;
&writecatemod;

} # end routine


##################################################################################
######## Subroutes ( Edit Category Name )


sub editcatname {


        if ($checkaction ne "yes") {

            # Grab the line to edit.

            $filetoopen = "$lbdir" . "data/allforums.cgi";
#    	    &winlock($filetoopen) if ($OS_USED eq "Nt");
            open(FILE,"$filetoopen");
#            flock(FILE, 1) if ($OS_USED eq "Unix");
            @forums = <FILE>;
            close(FILE);
#            &winunlock($filetoopen) if ($OS_USED eq "Nt");

            foreach $forum (@forums) {
            chomp $forum;
 	    next if ($forum eq "");
                ($tempno, $category, $categoryplace) = split(/\t/,$forum);
    	    	next if ($tempno !~ /^[0-9]+$/);
                    if ($incategory eq "$categoryplace" && $category !~/^childforum-[0-9]+/) {
                        ($trash, $categoryname, $notneeded) = split(/\t/,$forum);
                        }
                    }

            # Present the form to be filled in
               $catefiletoopen = "$lbdir" . "boarddata/catemod$incategory.cgi"; 
               open(CATEFILE,"$catefiletoopen"); 
               $catemods =<CATEFILE>;
               close(CATEFILE);


            print qq~
            <form action="$thisprog" method="post">
            <input type=hidden name="action" value="editcatname">
            <input type=hidden name="category" value="$incategory">
            <input type=hidden name="checkaction" value="yes">
            <tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF>
            <b>欢迎来到论坛管理中心 / 编辑分类名称</b>
            </td></tr>
            <tr>

            <tr>
            <td bgcolor=#EEEEEE align=center colspan=2>
            <font color=#990000><b>编辑 '$categoryname' 分类的名称</b>
            </td></tr>


            <tr>
            <td bgcolor=#FFFFFF width=40%>
            <font color=#333333><b>分类名称</b><br>请输入分类名称</font></td>
            <td bgcolor=#FFFFFF>
            <input type=text size=40 name="categoryname" value="$categoryname"></td>
            </tr>
            <tr> 
            <td bgcolor=#FFFFFF width=40%> 
            <font color=#333333><b>区版主</b><br>请输入管理此分类的区版主，如果您希望有多个区版主，请使用 "," (英文逗号，不是中文逗号)隔开。<BR><B>例如</B>：山鹰, 花无缺</font></td> 
            <td bgcolor=#FFFFFF> 
            <input type=text size=40 name="catemods" value="$catemods"></td> 
            </tr>

            <tr>
            <td bgcolor=#FFFFFF align=center colspan=2>
            <input type=submit value="提 交"></form></td></tr></table></td></tr></table>
            ~;
            } # end if

            else {

                # Grab the lines to change.
               my @catemolist = split(/\,/,$new_catemods); 
               foreach(@catemolist){ 
               chomp $_; 
               $_ =~ s/ /\_/g; 
               $_ =~ tr/A-Z/a-z/; 
               next if ($_ eq ""); 
	       my $namenumber = &getnamenumber($_);
	       &checkmemfile($_,$namenumber);
               if ((!(-e "${lbdir}$memdir/$namenumber/$_.cgi"))&&(!(-e "${lbdir}$memdir/old/$_.cgi"))) { &winunlock($filetoopen) if ($OS_USED eq "Nt"); &errorout("区版主名单中，$_ 这个用户 ID 是不存在的！"); } 
               }

                $filetoopen = "$lbdir" . "data/allforums.cgi";
#	        &winlock($filetoopen) if ($OS_USED eq "Nt");
                open(FILE,"$filetoopen");
#	        flock(FILE, 1) if ($OS_USED eq "Unix");
                @forums = <FILE>;
                close(FILE);

                # Lets remake the file with the new info

                $filetoopen = "$lbdir" . "data/allforums.cgi";
                open(FILE,">$filetoopen");
                flock(FILE,2) if ($OS_USED eq "Unix");
                foreach $forum (@forums) {
                    chomp $forum;
		    next if ($forum eq "");
                    ($tempno, $category, $categorynumber) = split(/\t/,$forum);
    	    	    next if ($tempno !~ /^[0-9]+$/);
                    if ($incategory eq "$categorynumber" && $category !~/^childforum-[0-9]+/) {
                        ($forumid, $category, $categoryplace, $forumname, $forumdescription, $forummoderator ,$htmlstate ,$idmbcodestate ,$privateforum, $startnewthreads ,$lastposter ,$lastposttime, $threads, $posts, $forumgraphic, $miscad2, $misc,$forumpass,$hiddenforum,$indexforum,$teamlogo,$teamurl, $fgwidth, $fgheight, $miscad4, $todayforumpost, $miscad5) = split(/\t/,$forum);
                        $linetochange = "$forumid\t$new_categoryname\t$incategory\t$forumname\t$forumdescription\t$forummoderator\t$htmlstate\t$idmbcodestate\t$privateforum\t$startnewthreads\t$lastposter\t$lastposttime\t$threads\t$posts\t$forumgraphic\t$miscad2\t$misc\t$forumpass\t$hiddenforum\t$indexforum\t$teamlogo\t$teamurl\t$fgwidth\t$fgheight\t$miscad4\t$todayforumpost\t$miscad5\t";
                        chomp $linetochange;
                        print FILE "$linetochange\n";
              	  	$dirtomake = "$lbdir" . "forum$forumid";
	                $filetomake1 = "$dirtomake/foruminfo.cgi";
          	        open(FILE1,">$filetomake1");
                        print FILE1 $linetochange;
                	close(FILE1);
                        $forumname = ""; $forumdescription = ""; $forummoderator = ""; $lastposter = ""; $lastposttime = ""; $threads = ""; $posts = ""; $forumgraphic = ""; $miscad2 = "";
                    }
                    else {
                        print FILE "$forum\n";
                    }
                }
                close (FILE);
#	        &winunlock($filetoopen) if ($OS_USED eq "Nt");

               $catefiletoopen = "$lbdir" . "boarddata/catemod$incategory.cgi"; 
               open(CATEFILE,">$catefiletoopen"); 
               print CATEFILE "$new_catemods\n"; 
               close(CATEFILE);

                print qq~
                <tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF>
                <b>欢迎来到论坛管理中心 / 编辑分类名称结果</b>
                </td></tr>
                <tr>
                <td bgcolor=#EEEEEE align=center colspan=2>
                <font color=#333333><b>所有信息已经成功保存</b>
                </td></tr></table></td></tr></table>
                ~;
&forumjump;
&writecatemod;

                } # end else

            } # end routine


##################################################################################
######## Subroutes ( Edit Category Name )


sub reordercats {


        if ($checkaction ne "yes") {

            print qq~
            <form action="$thisprog" method="post">
            <input type=hidden name="action" value="reordercategories">
            <input type=hidden name="checkaction" value="yes">
            <tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF>
            <b>欢迎来到论坛管理中心 / 论坛分类重新排序</b>
            </td></tr>
            <tr><td bgcolor=#FFFFFF" colspan=3><font color=#333333>
            <b>注意事项：</b><br><br>
            在此您可以将论坛分类重新排序。分类将按照数字重新显示。<BR><BR><b>1 表示此为第一分类，将显示在最前面</b>。<br><br>
            <b>提交之前请仔细检查所有设置，并保证没有重复数字，有重复将会导致有的分类无法显示！</b><br><br>
            <b>数字请注意不要用全角汉字的数字，而且必须大于0！</b><br><br>
            </td></tr>
            ~;

            $filetoopen = "$lbdir" . "data/allforums.cgi";
#	    &winlock($filetoopen) if ($OS_USED eq "Nt");
            open(FILE, "$filetoopen");
#	    flock(FILE, 1) if ($OS_USED eq "Unix");
            @forums = <FILE>;
            close(FILE);
#	    &winunlock($filetoopen) if ($OS_USED eq "Nt");

	    $a=0;
            foreach $forum (@forums) { #start foreach @forums
		$a  = sprintf("%09d",$a);
                chomp $forum;
                ($forumid, $category, $categoryplace, $forumname, $forumdescription, $forummoderator ,$htmlstate ,$idmbcodestate ,$privateforum, $startnewthreads ,$lastposter ,$lastposttime, $threads, $posts, $forumgraphic, $miscad2, $misc,$forumpass,$hiddenforum,$indexforum,$teamlogo,$teamurl, $fgwidth, $fgheight, $miscad4, $todayforumpost, $miscad5) = split(/\t/,$forum);
		$categoryplace  = sprintf("%09d",$categoryplace);
                $rearrange = ("$categoryplace\t$a\t$category\t$forumname\t$forumdescription\t$forumid\t$forumgraphic\t$miscad2\t$misc\t$forumpass\t$hiddenforum\t$indexforum$teamlogo\t$teamurl\t$fgwidth\t$fgheight\t$miscad4\t$todayforumpost\t$miscad5\t");
                push (@rearrangedforums, $rearrange);
		$a++;
            } # end foreach (@forums)

            @finalsortedforums = sort(@rearrangedforums);

            foreach $sortedforums (@finalsortedforums) { #start foreach @finalsortedforums
                ($categoryplace,my $a, $category, $forumgraphic, $miscad2, $misc, $forumpass,$hiddenforum,$indexforum,$teamlogo,$teamurl, $fgwidth, $fgheight, $miscad4, $todayforumpost, $miscad5) = split(/\t/,$sortedforums);
        	$categoryplace  = sprintf("%01d",$categoryplace);

                if ($categoryplace ne $lastcategoryplace) { #start if $categoryplace
                    print qq~
                    <tr>
                    <td bgcolor=#FFFFFF width=40%><font color=#333333>
                    <b>-=> $category</b></font></td>
                    <td bgcolor=#FFFFFF><font color=#333333>现在位置 [ <B>$categoryplace</B> ]，请输入新的数字以便排序：<input type=text size=4 maxlength=2 name="$categoryplace" value="$categoryplace">
                    </td></tr>
                    ~;
                    } # end if

                    $lastcategoryplace = $categoryplace;

                 } # end foreach



                    print qq~
                    <tr>
                    <td bgcolor=#EEEEEE align=center colspan=2>
                    <BR><input type=submit value="提 交"></td></form></tr></table></td></tr></table>
                    ~;

            } # end if


            else {

                # Grab the lines to change.

                $filetoopen = "$lbdir" . "data/allforums.cgi";
#		&winlock($filetoopen) if ($OS_USED eq "Nt");
                open(FILE,"$filetoopen");
#	        flock(FILE, 1) if ($OS_USED eq "Unix");
                @forums = <FILE>;
                close(FILE);

                foreach $forum (@forums) {
                    chomp $forum;
	 	    next if ($forum eq "");
                    ($tempno, $notneeded, $categorynumber) = split(/\t/,$forum);
    	    	    next if ($tempno !~ /^[0-9]+$/);
    	    	    chomp $PARAM{$categorynumber};
                    if (($PARAM{$categorynumber} !~ /^[0-9]+$/)||($PARAM{$categorynumber} < 0)) {

                	print qq~
                <tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF>
                <b>欢迎来到论坛管理中心 / 编辑分类名称结果</b>
                </td></tr>
                <tr>
                <td bgcolor=#EEEEEE align=center colspan=2>
                <font color=red><b>您输入的序号中有错误，请返回修正后再继续！</b>
                </td></tr></table></td></tr></table>
                ~;
			exit;
                    }
		}


                $filetoopen = "$lbdir" . "data/allforums.cgi";
                open(FILE,">$filetoopen");
                flock(FILE,2) if ($OS_USED eq "Unix");
                foreach $forum (@forums) {
                    chomp $forum;
	 	    next if ($forum eq "");
                    ($tempno, $notneeded, $categorynumber) = split(/\t/,$forum);
    	    	    next if ($tempno !~ /^[0-9]+$/);
                    $newid = $PARAM{$categorynumber};
                    ($forumid, $category, $categoryplace, $forumname, $forumdescription, $forummoderator ,$htmlstate ,$idmbcodestate ,$privateforum, $startnewthreads ,$lastposter ,$lastposttime, $threads, $posts, $forumgraphic, $miscad2, $misc,$forumpass,$hiddenforum,$indexforum,$teamlogo,$teamurl, $fgwidth, $fgheight, $miscad4, $todayforumpost, $miscad5) = split(/\t/,$forum);
                    print FILE "$forumid\t$category\t$newid\t$forumname\t$forumdescription\t$forummoderator\t$htmlstate\t$idmbcodestate\t$privateforum\t$startnewthreads\t$lastposter\t$lastposttime\t$threads\t$posts\t$forumgraphic\t$miscad2\t$misc\t$forumpass\t$hiddenforum\t$indexforum\t$teamlogo\t$teamurl\t$fgwidth\t$fgheight\t$miscad4\t$todayforumpost\t$miscad5\t\n";
                }

                close (FILE);
#	        &winunlock($filetoopen) if ($OS_USED eq "Nt");

foreach (@params) {
$catf = "${lbdir}boarddata/catemod$_.cgi";
if (-e $catf) { rename ($catf, "${catf}.pl"); }
$cattop = "${lbdir}boarddata/catontop$_.cgi"; 
if (-e $cattop) { rename($cattop,"$cattop.pl"); } 
}
foreach (@params) {
$catf="${lbdir}boarddata/catemod$_.cgi.pl";
if (-e $catf) {rename ($catf,"${lbdir}boarddata/catemod$PARAM{$_}.cgi");}
$cattop = "${lbdir}boarddata/catontop$_.cgi.pl"; 
if (-e $cattop) {rename ($cattop,"${lbdir}boarddata/catontop$PARAM{$_}.cgi");}
}

                print qq~
                <tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF>
                <b>欢迎来到论坛管理中心 / 编辑分类名称结果</b>
                </td></tr>
                <tr>
                <td bgcolor=#EEEEEE align=center colspan=2>
                <font color=#333333><b>所有信息已经成功保存</b>
                </td></tr></table></td></tr></table>
                ~;
&forumjump;
&writecatemod;
                } # end else


} # end routine

sub reorder {


        if ($checkaction ne "yes") {

            print qq~
            <form action="$thisprog" method="post">
            <input type=hidden name="action" value="reorder">
            <input type=hidden name="checkaction" value="yes">
            <input type=hidden name="category" value="$inforum">

            <tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF>
            <b>欢迎来到论坛管理中心 / 论坛重新排序</b>
            </td></tr>
            <tr><td bgcolor=#FFFFFF" colspan=3><font color=#333333>
            <b>注意事项：</b><br><br>
            在此您可以将分论坛重新排序。<br>分论坛将自动根据顺序重新改变顺序和分区名称
            </td></tr>~;
            $filetoopen = "$lbdir" . "data/allforums.cgi";
#         &winlock($filetoopen) if ($OS_USED eq "Nt");
         open(FILE,"$filetoopen");
#         flock(FILE, 1) if ($OS_USED eq "Unix");
         @forums = <FILE>;
         close(FILE);
#         &winunlock($filetoopen) if ($OS_USED eq "Nt");


         foreach $forum (@forums) {
            chomp $forum;
	    next if ($forum eq "");
            ($forumid,$category,$notneeded,$notneeded) = split(/\t/,$forum);
    	    next if ($forumid !~ /^[0-9]+$/);
                if ($forumid eq $inforum) {
                    ($forumid, $mycategory, $mycategoryplace, $myforumname, $forumdescription, $forummoderator ,$htmlstate ,$idmbcodestate ,$privateforum, $startnewthreads ,$lastposter ,$lastposttime, $threads, $posts, $forumgraphic, $miscad2, $misc,$forumpass,$hiddenforum,$indexforum,$teamlogo,$teamurl, $fgwidth, $fgheight, $miscad4, $todayforumpost, $miscad5) = split(/\t/,$forum);
                    last;
                }
         }
         $childmove=($mycategory =~/^childforum-[0-9]+$/)?1:0;
            print qq~
            <tr><td><input type="radio" name="movetype" value="tomove" checked>把论坛 <font color=red>$myforumname</font> 移到论坛
            <select name="forum">
            ~;



$a=0;
foreach my $forum (@forums) { #start foreach @forums
    $a  = sprintf("%09d",$a);
    chomp $forum;
    next if ($forum eq "");
    (my $forumid, my $category, my $categoryplace, my $forumname, my $forumdescription) = split(/\t/,$forum);
    next if ($forumid !~ /^[0-9]+$/);
    next if ($categoryplace !~ /^[0-9]+$/);
    next if ($forumid eq $inforum);
#    next if ($category =~/childforum-[0-9]+/);
    $categoryplace  = sprintf("%09d",$categoryplace);
    $rearrange = ("$categoryplace\t$a\t$category\t$forumname\t$forumdescription\t$forumid\t$forumgraphic\t$miscad2\t$misc\t$forumpass\t$hiddenforum\t$indexforum\t$teamlogo\t$teamurl\t$fgwidth\t$fgheight\t$miscad4\t$todayforumpost\t$miscad5\t");
    push (@rearrangedforums, $rearrange);
    $a++;
}

@finalsortedforums = sort (@rearrangedforums);
foreach my $sortedforums (@finalsortedforums) {
    (my $categoryplace,my $a, my $category, my $forumname, my $forumdescription, my $forumid, my $forumgraphic, my $miscad2, my $misc, my $forumpass, my $hiddenforum, my $indexforum,my $teamlogo,my $teamurl,my $fgwidth,my $fgheight,my $miscad4,my $todayforumpost,my $miscad5) = split(/\t/,$sortedforums);
    $categoryplace  = sprintf("%01d",$categoryplace);
    if ($category eq $mycategory){
	$jumphtml3 = "<option value=\"top$categoryplace\">╋子论坛列表最顶\n" if ($jumphtml3 eq "");
        $jumphtml3 .= "<option value=\"$forumid\">├$forumname\n";
    }
#    else {$jumphtml3 .= "<option value=\"$forumid\">├$category eq $mycategory\n"; }
    next if ($category =~/childforum-[0-9]+/);

    if ($categoryplace ne $lastcategoryplace) {
        $jumphtml .= "<option value=\"top$forumid\" style=background-color:$titlecolor>╋$category\n";
    }
    if (($forumname ne $myforumname)||($categoryplace ne $mycategoryplace)){
        $jumphtml .= "<option value=\"$forumid\">　├$forumname\n";
    }

    $lastcategoryplace = $categoryplace;
}
$jumphtml .= qq~</select>\n~;
$jumphtml2=$jumphtml;
$jumphtml2=~s/<option value="top(.+?)" style=background-color:$titlecolor>╋(.+?)\n//g;
$jumphtml2=~s/　├//g;




                    print qq~
                    $jumphtml下，并且自动改变分区属性。
                   </td></tr>
~;
                   	if($childmove){
                    print qq~
                   	<tr><td><input type="radio" name="movetype" value="movechild">把子论坛 <font color=red>$myforumname</font> 移到<select name="indexforum">$jumphtml3</select>下。</td></tr>~;
                   	}
                    print qq~                   	<tr><td><input type="radio" name="movetype" value="tochild">把论坛 <font color=red>$myforumname</font> 成为<select name="cforum">$jumphtml2的子论坛，并且自动改变分区属性。</td></tr>
                   	<tr>
                    <tr>
                    <td bgcolor=#EEEEEE align=center colspan=2>
                    <BR><input type=submit value="提 交"></td></form></tr></table></td></tr></table>
                    ~;

            } # end if


            else {

                # Grab the lines to change.

                $filetoopen = "$lbdir" . "data/allforums.cgi";
#		&winlock($filetoopen) if ($OS_USED eq "Nt");
                open(FILE,"$filetoopen");
#	        flock(FILE, 1) if ($OS_USED eq "Unix");
                @forums = <FILE>;
                close(FILE);

            foreach $forum (@forums) {
            	chomp $forum;
	    	next if ($forum eq "");
            	($forumid,$category,$categoryplace,$notneeded) = split(/\t/,$forum);
    	    	next if ($forumid !~ /^[0-9]+$/);
    	    	next if ($categoryplace !~ /^[0-9]+$/);
                if ($forumid eq "$incategory") {
                    ($oldforumid, $oldcategory, $oldcategoryplace, $oldmyforumname, $oldforumdescription, $oldforummoderator ,$oldhtmlstate ,$oldidmbcodestate ,$oldprivateforum, $oldstartnewthreads ,$oldlastposter ,$oldlastposttime, $oldthreads, $oldposts, $oldforumgraphic, $oldratings, $oldmisc,$oldforumpass,$oldhiddenforum,$oldindexforum,$oldteamlogo,$oldteamurl, $oldfgwidth, $oldfgheight, $oldmiscad4, $oldtodayforumpostno, $oldmiscad5) = split(/\t/,$forum);
                }elsif($category eq "childforum-$incategory"){
                push(@childforum,$forum);
                }elsif($category eq "childforum-$inforum"){
                push(@ochildforum,$forum);
                }
            }
				chomp @childforum,@ochildforum;

                $filetoopen = "$lbdir" . "data/allforums.cgi";
                open(FILE,">$filetoopen");
#                flock(FILE,2) if ($OS_USED eq "Unix");
    	    	   if($inmovetype eq "tomove"){
                foreach $forum (@forums) {
                    chomp $forum;
	 	    next if ($forum eq "");
                    ($forumid, $category, $categoryplace, $myforumname, $forumdescription, $forummoderator ,$htmlstate ,$idmbcodestate ,$privateforum, $startnewthreads ,$lastposter ,$lastposttime, $threads, $posts, $forumgraphic, $miscad2, $misc,$forumpass,$hiddenforum,$indexforum,$teamlogo,$teamurl, $fgwidth, $fgheight, $miscad4, $todayforumpost, $miscad5) = split(/\t/,$forum);
    	    	    next if ($forumid !~ /^[0-9]+$/);
                    if ($forumid ne $incategory && $category ne "childforum-$incategory" && $category ne "childforum-$inforum"){
                	if ($forumid eq $inforum){
                  	  print FILE "$forum\n";
                	  foreach(@ochildforum){
                  	  print FILE "$_\n";
                	  }
                  	  print FILE "$oldforumid\t$category\t$categoryplace\t$oldmyforumname\t$oldforumdescription\t$oldforummoderator\t$oldhtmlstate\t$oldidmbcodestate\t$oldprivateforum\t$oldstartnewthreads\t$oldlastposter\t$oldlastposttime\t$oldthreads\t$oldposts\t$oldforumgraphic\t$oldratings\t$oldmisc\t$oldforumpass\t$oldhiddenforum\t$oldindexforum\t$oldteamlogo\t$oldteamurl\t$oldfgwidth\t$oldfgheight\t$oldmiscadd4\t$oldtodayforumpostno\t$oldmiscad5\t\n";

	                  $filetomake1 = "$lbdir" . "forum$oldforumid/foruminfo.cgi";
          	          open(FILE1,">$filetomake1");
                  	  print FILE1 "$oldforumid\t$category\t$categoryplace\t$oldmyforumname\t$oldforumdescription\t$oldforummoderator\t$oldhtmlstate\t$oldidmbcodestate\t$oldprivateforum\t$oldstartnewthreads\t$oldlastposter\t$oldlastposttime\t$oldthreads\t$oldposts\t$oldforumgraphic\t$oldratings\t$oldmisc\t$oldforumpass\t$oldhiddenforum\t$oldindexforum\t$oldteamlogo\t$oldteamurl\t$oldfgwidth\t$oldfgheight\t$oldmiscadd4\t$oldtodayforumpostno\t$oldmiscad5\t";
                	  close(FILE1);
                	  foreach(@childforum){
                	  	  @childdata=split(/\t/,$_);
                	  	  chomp @childdata;
                	  	  $childdata[2]=$categoryplace;
                	  	  $childdata=join("\t",@childdata);
                  	  print FILE "$childdata\t\n";
	                  $filetomake1 = "$lbdir" . "forum$childdata[1]/foruminfo.cgi";
          	          open(FILE1,">$filetomake1");
                  	  print FILE1 "$childdata\t";
                	  close(FILE1);
                	  }
         		}
              		elsif ("top$forumid" eq $inforum) {
                	  print FILE "$oldforumid\t$category\t$categoryplace\t$oldmyforumname\t$oldforumdescription\t$oldforummoderator\t$oldhtmlstate\t$oldidmbcodestate\t$oldprivateforum\t$oldstartnewthreads\t$oldlastposter\t$oldlastposttime\t$oldthreads\t$oldposts\t$oldforumgraphic\t$oldratings\t$oldmisc\t$oldforumpass\t$oldhiddenforum\t$oldindexforum\t$oldteamlogo\t$oldteamurl\t$oldfgwidth\t$oldfgheight\t$oldmiscadd4\t$oldtodayforumpostno\t$oldmiscad5\t\n";
	                  $filetomake1 = "$lbdir" . "forum$oldforumid/foruminfo.cgi";
          	          open(FILE1,">$filetomake1");
                	  print FILE1 "$oldforumid\t$category\t$categoryplace\t$oldmyforumname\t$oldforumdescription\t$oldforummoderator\t$oldhtmlstate\t$oldidmbcodestate\t$oldprivateforum\t$oldstartnewthreads\t$oldlastposter\t$oldlastposttime\t$oldthreads\t$oldposts\t$oldforumgraphic\t$oldratings\t$oldmisc\t$oldforumpass\t$oldhiddenforum\t$oldindexforum\t$oldteamlogo\t$oldteamurl\t$oldfgwidth\t$oldfgheight\t$oldmiscadd4\t$oldtodayforumpostno\t$oldmiscad5\t";
                	  close(FILE1);
                	  foreach(@childforum){
                	  	  @childdata=split(/\t/,$_);
                	  	  chomp @childdata;
                	  	  $childdata[2]=$categoryplace;
                	  	  $childdata=join("\t",@childdata);
                  	  print FILE "$childdata\t\n";
	                  $filetomake1 = "$lbdir" . "forum$childdata[1]/foruminfo.cgi";
          	          open(FILE1,">$filetomake1");
                  	  print FILE1 "$childdata\t";
                	  close(FILE1);
                	  }
                	  print FILE "$forum\n";
              		}
             	    	else {
        			print FILE "$forum\n";
               	    	}
        	    }
        	}
    	    	   }
elsif($inmovetype eq "movechild"){
$newforuminfo="$oldforumid\t$oldcategory\t$oldcategoryplace\t$oldmyforumname\t$oldforumdescription\t$oldforummoderator\t$oldhtmlstate\t$oldidmbcodestate\t$oldprivateforum\t$oldstartnewthreads\t$oldlastposter\t$oldlastposttime\t$oldthreads\t$oldposts\t$oldforumgraphic\t$oldratings\t$oldmisc\t$oldforumpass\t$oldhiddenforum\t$oldindexforum\t$oldteamlogo\t$oldteamurl\t$oldfgwidth\t$oldfgheight\t$oldmiscadd4\t$oldtodayforumpostno\t$oldmiscad5\t\n";
                foreach $forum (@forums) {
                    chomp $forum;
                    next if ($forum eq "");
					($forumid,my $category, my $categoryplace, undef) = split(/\t/,$forum);
					next if ($forumid !~ /^[0-9]+$/);
					next if ($forumid eq $oldforumid);
					print FILE "$forum\n";
					if("top$categoryplace" eq $new_indexforum && $writeinfo ne 1) { print FILE $newforuminfo; $writeinfo = 1; }
					print FILE $newforuminfo if($forumid eq $new_indexforum);
                }
    	    	   }    	    	   
    	    	   else{
                foreach $forum (@forums) {
                    chomp $forum;
	 	    next if ($forum eq "");
                    ($forumid, $category, $categoryplace, $myforumname, $forumdescription, $forummoderator ,$htmlstate ,$idmbcodestate ,$privateforum, $startnewthreads ,$lastposter ,$lastposttime, $threads, $posts, $forumgraphic, $miscad2, $misc,$forumpass,$hiddenforum,$indexforum,$teamlogo,$teamurl, $fgwidth, $fgheight, $miscad4, $todayforumpost, $miscad5) = split(/\t/,$forum);
    	    	    next if ($forumid !~ /^[0-9]+$/);
                    if ($forumid ne $incategory){
                	if ($forumid eq $incforum){
                  	  print FILE "$forum\n";
                  	  print FILE "$oldforumid\tchildforum-$incforum\t$categoryplace\t$oldmyforumname\t$oldforumdescription\t$oldforummoderator\t$oldhtmlstate\t$oldidmbcodestate\t$oldprivateforum\t$oldstartnewthreads\t$oldlastposter\t$oldlastposttime\t$oldthreads\t$oldposts\t$oldforumgraphic\t$oldratings\t$oldmisc\t$oldforumpass\t$oldhiddenforum\t$oldindexforum\t$oldteamlogo\t$oldteamurl\t$oldfgwidth\t$oldfgheight\t$oldmiscadd4\t$oldtodayforumpostno\t$oldmiscad5\t\n";

                	  $dirtomake = "$lbdir" . "forum$oldforumid";
	                  $filetomake1 = "$dirtomake/foruminfo.cgi";
          	          open(FILE1,">$filetomake1");
                  	  print FILE1 "$oldforumid\tchildforum-$incforum\t$categoryplace\t$oldmyforumname\t$oldforumdescription\t$oldforummoderator\t$oldhtmlstate\t$oldidmbcodestate\t$oldprivateforum\t$oldstartnewthreads\t$oldlastposter\t$oldlastposttime\t$oldthreads\t$oldposts\t$oldforumgraphic\t$oldratings\t$oldmisc\t$oldforumpass\t$oldhiddenforum\t$oldindexforum\t$oldteamlogo\t$oldteamurl\t$oldfgwidth\t$oldfgheight\t$oldmiscadd4\t$oldtodayforumpostno\t$oldmiscad5\t";
                	  close(FILE1);
                	}elsif($category eq "childforum-$oldforumid"){
                  	  print FILE "$forumid\tchildforum-$incforum\t$categoryplace\t$myforumname\t$forumdescription\t$forummoderator\t$htmlstate\t$idmbcodestate\t$privateforum\t$startnewthreads\t$lastposter\t$lastposttime\t$threads\t$posts\t$forumgraphic\t$miscad2\t$misc\t$forumpass\t$hiddenforum\t$indexforum\t$teamlogo\t$teamurl\t$fgwidth\t$fgheight\t$miscad4\t$todayforumpost\t$miscad5\t\n";

                	  $dirtomake = "$lbdir" . "forum$forumid";
	                  $filetomake1 = "$dirtomake/foruminfo.cgi";
          	          open(FILE1,">$filetomake1");
                  	  print FILE1 "$forumid\tchildforum-$incforum\t$categoryplace\t$myforumname\t$forumdescription\t$forummoderator\t$htmlstate\t$idmbcodestate\t$privateforum\t$startnewthreads\t$lastposter\t$lastposttime\t$threads\t$posts\t$forumgraphic\t$miscad2\t$misc\t$forumpass\t$hiddenforum\t$indexforum\t$teamlogo\t$teamurl\t$fgwidth\t$fgheight\t$miscad4\t$todayforumpost\t$miscad5\t";
                	  close(FILE1);
                	}else {
        			print FILE "$forum\n";
                	}
                    }
                }
    	    	   }

                close (FILE);
#	        &winunlock($filetoopen) if ($OS_USED eq "Nt");

                print qq~
                <tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF>
                <b>欢迎来到论坛管理中心 / 分论坛排序名称结果</b>
                </td></tr>
                <tr>
                <td bgcolor=#EEEEEE align=center colspan=2>
                <font color=#333333><b>所有信息已经成功保存</b>
                </td></tr></table></td></tr></table>
                ~;
&forumjump;

                } # end else


}

sub errorout {
    print qq~<tr><td bgcolor=#2159C9 colspan=2><font color=#FFFFFF><b>欢迎来到论坛管理中心 / 发生错误</b></td></tr>
<tr><td bgcolor=#FFFFFF colspan=2><font color=#333333><b>$_[0]</b></td></tr></table></td></tr></table>
~;
    exit;
}

sub forumjump {
    unlink "${lbdir}wap/leoM.cgi";
    my $hidden;
    $jumphtml .= qq~<SCRIPT LANGUAGE="JavaScript">
function surfto1(list){
var myindex1  = document.jump.selectedIndex;
if (myindex1 != 0){
var URL = document.jump.jumpto.options[document.jump.jumpto.selectedIndex].value;
top.location.href = URL; target = '_self';
}}
</SCRIPT>
<form action="forums.cgi" method="post" name="jump">
<select name="jumpto" onchange="surfto1(this)">
<option value="leobbs.cgi">跳转论坛至...</option>
~;

	open(FILE, "${lbdir}data/allforums.cgi");
	sysread(FILE, my $forums,(stat(FILE))[7]);
	close(FILE);
        $forums =~ s/\r//isg;
	@forums = split (/\n/,$forums);

    $a=0;
    @rearrangedforums=();
    foreach my $forum (@forums) { #start foreach @forums
	$a  = sprintf("%09d",$a);
	chomp $forum;
	next if ($forum eq "");
	(my $forumid, my $category, my $categoryplace, my $forumname, my $forumdescription, my $tmp , $tmp , $tmp , $tmp,  $tmp , $tmp , $tmp,  $tmp,  $tmp,  $tmp, $tmp, $tmp, $tmp,my $hiddenforum,$tmp,$tmp,$tmp, $tmp, $tmp, $tmp, $tmp, $tmp) = split(/\t/,$forum);
	next if ($forumid !~ /^[0-9]+$/);
	next if ($categoryplace !~ /^[0-9]+$/);
	$categoryplace  = sprintf("%09d",$categoryplace);
	$rearrange = ("$categoryplace\t$a\t$category\t$forumname\t$forumdescription\t$forumid\t$forumgraphic\t$miscad2\t$forumpass\t$hiddenforum\t$indexforum\t");
	push (@rearrangedforums, $rearrange);
	$a++;
    }

    @finalsortedforums = sort (@rearrangedforums);
$outputbutton = "";
foreach my $sortedforums (@finalsortedforums) {
    (my $categoryplace, my $a, my $category, my $forumname, my $forumdescription, my $forumid, my $forumgraphic, my $miscad2, my $forumpass, my $hiddenforum, my $indexforum) = split(/\t/,$sortedforums);
    $categoryplace  = sprintf("%01d",$categoryplace);
    if ($categoryplace ne $lastcategoryplace) {
    	    $jumphtml .= "<option value=\"category.cgi?category=$categoryplace\" style=background-color:\$titlecolor>╋$category\n</option>";
#            $jumphtml .= "<option value=\"forums.cgi?forum=$forumid\" style=background-color:\$titlecolor>╋$category\n</option>";
    }
    if ($hiddenforum eq "yes"){ $hidden="(隐含)"; }else{ $hidden=""; } 
    if ($category !~ /^childforum-[0-9]+/) {
	if ($hidden ne "") {
	    $jumphtml .= "<!--h <option value=\"forums.cgi?forum=$forumid\">　|-$forumname$hidden\n</option> -->";
	    $outputbutton .= "<!--h <option value=\"$forumid\">　|-$forumname$hidden\n</option> -->";
	    $fname.="\$fname$forumid=\"$forumname\";\n";
	} else {
	    $jumphtml .= "<option value=\"forums.cgi?forum=$forumid\">　|-$forumname\n</option>";
	    $outputbutton .= "<option value=\"$forumid\">　|-$forumname\n</option>";
	    $fname.="\$fname$forumid=\"$forumname\";\n";
	}
    }
    else {
        if ($hidden ne "") {
            $jumphtml .= "<!--h <!--c <option value=\"forums.cgi?forum=$forumid\">　|　|-$forumname$hidden\n</option> --> -->";
            $outputbutton .= "<!--h <!--c <option value=\"$forumid\">　|　|-$forumname$hidden\n</option> --> -->";
            $fname.="\$fname$forumid=\"$forumname\";\n";
        } else {
            $jumphtml .= "<!--c <option value=\"forums.cgi?forum=$forumid\">　|　|-$forumname$hidden\n</option> -->";
            $outputbutton .= "<!--c <option value=\"$forumid\">　|　|-$forumname$hidden\n</option> -->";
            $fname.="\$fname$forumid=\"$forumname\";\n";
        }
    }
    $lastcategoryplace = $categoryplace;
}
$jumphtml .= qq~</select>\n~;

mkdir ("${lbdir}cache", 0777) if (!(-e "${lbdir}cache"));
mkdir ("${lbdir}cache/myinfo", 0777) if (!(-e "${lbdir}cache/myinfo"));
mkdir ("${lbdir}cache/mymsg", 0777) if (!(-e "${lbdir}cache/mymsg"));
mkdir ("${lbdir}cache/meminfo", 0777) if (!(-e "${lbdir}cache/meminfo"));
mkdir ("${lbdir}cache/online", 0777) if (!(-e "${lbdir}cache/online"));
open (FILE, ">${lbdir}data/forumjump.pl");
$jumphtml  =~ s/\\/\\\\/isg;
$jumphtml  =~ s/~/\\\~/isg;
$jumphtml  =~ s/\$/\\\$/isg;
$jumphtml  =~ s/\@/\\\@/isg;
print FILE qq(\$jumphtml = qq~$jumphtml~;\n);
print FILE "1;\n";
close (FILE);
open (FILE, ">${lbdir}data/outputbutton.pl");
$outputbutton  =~ s/\\/\\\\/isg;
$outputbutton  =~ s/~/\\\~/isg;
$outputbutton  =~ s/\$/\\\$/isg;
$outputbutton  =~ s/\@/\\\@/isg;
print FILE qq(\$outputbutton = qq~$outputbutton~;\n);
print FILE "1;\n";
close (FILE);

open (FILE, ">${lbdir}data/fname.pl");
$fname  =~ s/\\/\\\\/isg;
$fname  =~ s/~/\\\~/isg;
$fname  =~ s/\@/\\\@/isg;
print FILE "$fname";
print FILE "1;\n";
close (FILE);

opendir (CATDIR, "${lbdir}cache");
@dirdata = readdir(CATDIR);
closedir (CATDIR);
@dirdata1 = grep(/forumcache/,@dirdata);
foreach (@dirdata1) { unlink ("${lbdir}cache/$_"); }

@dirdata = grep(/^forums/,@dirdata);
foreach (@dirdata) { unlink ("${lbdir}cache/$_"); }
}

sub writecatemod {
	opendir (CATDIR, "${lbdir}boarddata");
	@dirdata = readdir(CATDIR);
	closedir (CATDIR);
	@dirdata = grep(/^catemod/,@dirdata);
	foreach (@dirdata) {
   	    if (open(CATEFILE,"${lbdir}boarddata/$_")) {
   	        my $catemods =<CATEFILE>;
   	        close(CATEFILE);
   	        my @catemodnames = split(/\,/, $catemods);
   	        my $cmodnumber=@catemodnames;
	        foreach (@catemodnames) {
   		    chomp $_;
   		    next if ($_ eq "");
	            my $cleanedmodname = $_;
	            $cleanedmodname =~ s/ /\_/g;
	            $cleanedmodname =~ tr/A-Z/a-z/;
   		    $cmodoutput .= qq~<option value="~ . uri_escape($cleanedmodname) . qq~">$_</option>~;
	        }
	    }
	    if ($cmodoutput ne "") {
	    	$_ =~ s/^catemod(.+?)\.cgi$/$1/isg;
	        $cmodoutputfile .= qq~\$cmodoutput[$_] = qq(<img src=$imagesurl/images/team2.gif width=19 align=absmiddle><select onchange="surfto(this)"><option style=background-color:\$titlecolor>此分类区版主：</option>$cmodoutput);
~;
	        $cmodoutput = "";
	    }
	}

	mkdir ("${lbdir}cache", 0777) if (!(-e "${lbdir}cache"));
	mkdir ("${lbdir}cache/myinfo", 0777) if (!(-e "${lbdir}cache/myinfo"));
    	mkdir ("${lbdir}cache/mymsg", 0777) if (!(-e "${lbdir}cache/mymsg"));
	mkdir ("${lbdir}cache/meminfo", 0777) if (!(-e "${lbdir}cache/meminfo"));
	mkdir ("${lbdir}cache/online", 0777) if (!(-e "${lbdir}cache/online"));
    	mkdir ("${lbdir}cache/id", 0777) if (!(-e "${lbdir}cache/id"));
	open (FILE, ">${lbdir}data/forumcate.pl");
	$cmodoutputfile  =~ s/~/\\\~/isg;
	print FILE qq~$cmodoutputfile~;
	print FILE "1;\n";
	close (FILE);
opendir (CATDIR, "${lbdir}cache");
@dirdata = readdir(CATDIR);
closedir (CATDIR);
@dirdata = grep(/^forums/,@dirdata);
foreach (@dirdata) { unlink ("${lbdir}cache/$_"); }
}


#处理后台上传logo，By Easunlee
sub douppics
{ #1
  # $addme=$query->upload('addme'); #如果CGI.pm版本>2.47，推荐使用
  $addme=$query->param('addme'); #如果CGI.pm版本<2.47，用他替换上句
  return unless ($addme);

  my ($tmpfilename) = $addme =~ m|([^/:\\]+)$|; #注意,获取文件名字的形式变化
  my @filename = split(/\./,$tmpfilename); #注意
  my $up_name = $filename[0];
  my $up_ext = $filename[-1];
  $up_ext = lc($up_ext);

  &errorout("上传出错！不支持您所上传的图片类型，请重新选择！") if (($up_ext ne "gif") && ($up_ext ne "jpg") && ($up_ext ne "bmp")&&($up_ext ne "swf")&&($up_ext ne "png"));


  my $buffer;
  open (FILE,">$imagesdir/myimages/$up_name.$up_ext");
  binmode (FILE);
  binmode ($addme); #注意

  while (read($addme,$buffer,4096) )
  {#2
   print FILE $buffer;
   $filesize=$filesize+4;
  } #2
  close (FILE);
  close ($addme); #注意

  if ($up_ext eq "gif"||$up_ext eq "jpg"||$up_ext eq "bmp"||$up_ext eq "jpeg"||$up_ext eq "png"||$up_ext eq "ppm"||$up_ext eq "svg"||$up_ext eq "xbm"||$up_ext eq "xpm")
  { #3

     my $info = image_info("${imagesdir}myimages/$up_name.$up_ext");
     if ($info->{error} eq "Unrecognized file format")
     {
        unlink ("${imagesdir}myimages/$up_name.$up_ext");
        &errorout("上传出错&上传文件不是图片文件，请上传标准的图片文件！");
     }
     undef $info;
  } #3

} #1

