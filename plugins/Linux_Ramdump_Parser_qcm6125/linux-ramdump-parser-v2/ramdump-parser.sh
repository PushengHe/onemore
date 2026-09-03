# ramdump-parser.sh
  
#! /bin/bash
echo ""
echo "Start ramdump parser.."
  
local_path=$PWD
ramdump=$local_path/
vmlinux=$local_path/vmlinux
out=$local_path/out
  
gdb=/home/simon/work/codebase/SA6125_Android10.0_R01_c25_r003/SA6125_Android10.0_R01_c25_r003/prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9/bin/aarch64-linux-android-gdb
nm=/home/simon/work/codebase/SA6125_Android10.0_R01_c25_r003/SA6125_Android10.0_R01_c25_r003/prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9/bin/aarch64-linux-android-nm
objdump=/home/simon/work/codebase/SA6125_Android10.0_R01_c25_r003/SA6125_Android10.0_R01_c25_r003/prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9/bin/aarch64-linux-android-objdump

# git clone https://gitlab.com/quicla/platform/vendor/qcom-opensource/tools.git
ramparse_dir=/home/simon/work/pro_tools/linux-ramdump-parser-v2
########################################################################################
  
echo "cd $ramparse_dir"
cd $ramparse_dir
echo ""
  
echo -e "python ramparse.py -v $vmlinux -g $gdb  -n $nm  -j $objdump -a $ramdump -o $out -x"
#echo -e "python ramparse.py -v $vmlinux  -n $nm  -j $objdump -a $ramdump -o $out -x"
echo ""
  
# Python 3.8.10
#python ramparse.py -v $vmlinux -g $gdb  -n $nm  -j $objdump -a $ramdump -o $out -x
python3 ramparse.py -v $vmlinux -g $gdb  -n $nm  -j $objdump -a $ramdump -o $out -x --force-hardware trinket
#python ramparse.py -v $vmlinux  -n $nm  -j $objdump -a $ramdump -o $out -x
  
cd $local_path
echo "out: $out"
echo ""
exit 0
