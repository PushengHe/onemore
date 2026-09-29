import os


toolchain_bin_dir = os.path.abspath(os.path.join(
	os.path.dirname(__file__), '..', '..', '..', 'tools', 'gnu-tools', 'bin'
))

gdb64_path = os.path.join(toolchain_bin_dir, 'aarch64-linux-gnu-gdb.exe')
nm64_path = os.path.join(toolchain_bin_dir, 'aarch64-linux-gnu-nm.exe')
objdump64_path = os.path.join(toolchain_bin_dir, 'aarch64-linux-gnu-objdump.exe')

'''
gdb_path - absolute path to the gdb tool for the ramdumps
nm_path - absolute path to the gdb tool for the ramdumps
gdb64_path - absolute path to the 64-bit gdb tool for the ramdumps
nm64_path - absolute path to the 64-bit nm tool for the ramdumps
'''
