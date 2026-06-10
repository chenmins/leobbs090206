#####################################################
#  LEO SuperCool BBS / LeoBBS X / 雷傲极酷超级论坛  #
#####################################################
# 基于山鹰(糊)、花无缺制作的 LB5000 XP 2.30 免费版  #
#   新版程序制作 & 版权所有: 雷傲科技 (C)(R)2004    #
#####################################################
#      主页地址： http://www.LeoBBS.com/            #
#      论坛地址： http://bbs.LeoBBS.com/            #
#####################################################
#CGItempXXXXX

sub cleanolddata {
    my $ctime = time;
    opendir (DIRS, "${lbdir}cache/online");
    my @files = readdir(DIRS);
    closedir (DIRS);
    my $ci = 1;
    foreach (@files) {
    	unlink ("${lbdir}cache/online/$_") if ((-M "${lbdir}cache/online/$_") *86400 > 600);
    	$ci ++;
    	last if ($ci > 100);
    }
    &cleanolddata1 if ($ci < 60);
}

sub cleanolddata1 {
    opendir (DIRS, "${lbdir}");
    my @files = readdir(DIRS);
    closedir (DIRS);
    @files = grep(/^CGItemp/i, @files);
    foreach (@files) {
    	unlink ("${lbdir}$_") if ((-M "${lbdir}$_") *86400 > 600);
    	$ci ++;
    	last if ($ci > 20);
    }

    my $ctime = time;
    opendir (DIRS, "${lbdir}cache/id");
    my @files = readdir(DIRS);
    closedir (DIRS);
    my $ci = 1;
    foreach (@files) {
    	unlink ("${lbdir}cache/id/$_") if ((-M "${lbdir}cache/id/$_") *86400 > 600);
    	$ci ++;
    	last if ($ci > 110);
    }

    opendir (DIRS, "${lbdir}lock");
    my @files = readdir(DIRS);
    closedir (DIRS);
    @files = grep(/\.lck$/i, @files);
    foreach (@files) {
    	unlink ("${lbdir}lock/$_") if ((-M "${lbdir}lock/$_") *86400 > 60);
    	$ci ++;
    	last if ($ci > 130);
    }
}

sub cleanolddata2 {
    my $ctime = time;
    opendir (DIRS, "${lbdir}cache/myinfo");
    my @files = readdir(DIRS);
    closedir (DIRS);
    my $ci = 1;
    foreach (@files) {
    	unlink ("${lbdir}cache/myinfo/$_") if ((-M "${lbdir}cache/myinfo/$_") > 1);
    	$ci ++;
    	last if ($ci > 100);
    }
}

sub cleanolddata3 {
    my $ctime = time;
    opendir (DIRS, "${lbdir}cache/mymsg");
    my @files = readdir(DIRS);
    closedir (DIRS);
    my $ci = 1;
    foreach (@files) {
    	unlink ("${lbdir}cache/mymsg/$_") if ((-M "${lbdir}cache/mymsg/$_") > 3);
    	$ci ++;
    	last if ($ci > 100);
    }
}

sub cleanolddata4 {
    my $ctime = time;
    opendir (DIRS, "${lbdir}cache/meminfo");
    my @files = readdir(DIRS);
    closedir (DIRS);
    my $ci = 1;
    foreach (@files) {
    	unlink ("${lbdir}cache/meminfo/$_") if ((-M "${lbdir}cache/meminfo/$_") > 3);
    	$ci ++;
    	last if ($ci > 100);
    }
    &cleanolddata if ($ci < 60);
}
1;
