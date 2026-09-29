from pathlib import Path


def find_kaslr_offset(vmlinux_path, elf_path):
    from elftools.elf.elffile import ELFFile

    with Path(vmlinux_path).open('rb') as vmlinux_file, Path(elf_path).open('rb') as dump_file:
        vmlinux = ELFFile(vmlinux_file)
        symbol_table = vmlinux.get_section_by_name('.symtab')
        symbols = symbol_table.get_symbol_by_name('linux_banner') if symbol_table else None
        if not symbols:
            raise ValueError('vmlinux 缺少 linux_banner 符号')
        banner_address = symbols[0]['st_value']
        for segment in vmlinux.iter_segments():
            if segment['p_vaddr'] <= banner_address < segment['p_vaddr'] + segment['p_filesz']:
                vmlinux_file.seek(segment['p_offset'] + banner_address - segment['p_vaddr'])
                banner = vmlinux_file.read(512).split(b'\0', 1)[0]
                break
        else:
            raise ValueError('vmlinux 中无法读取 linux_banner')
        if not banner.startswith(b'Linux version '):
            raise ValueError('vmlinux 中的 linux_banner 无效')

        dump = ELFFile(dump_file)
        for segment in dump.iter_segments():
            if segment['p_type'] != 'PT_LOAD':
                continue
            position = segment.data().find(banner)
            if position >= 0:
                return segment['p_vaddr'] + position - banner_address
    raise ValueError('ap_minidump.elf 中找不到与 vmlinux 匹配的 linux_banner')


def build_ramparse_command(python_path, parser_path, vmlinux_path, dump_dir, analysis_dir):
    dump_dir = Path(dump_dir)
    command = [
        str(python_path), '-u', str(parser_path),
        '--vmlinux', str(vmlinux_path),
        '--ram-elf', str(dump_dir / 'ap_minidump.elf'),
        '--force-hardware', 'trinket', '--minidump', '-x',
        '-o', str(analysis_dir),
    ]

    if not (dump_dir / 'ap_minidump.elf').is_file():
        raise FileNotFoundError(dump_dir / 'ap_minidump.elf')
    kaslr_offset = find_kaslr_offset(vmlinux_path, dump_dir / 'ap_minidump.elf')
    if kaslr_offset:
        command.extend(['--kaslr-offset', hex(kaslr_offset)])

    segments = {}
    with (dump_dir / 'dump_info.txt').open(encoding='utf-8') as dump_info:
        for line in dump_info:
            fields = line.split()
            if len(fields) < 4:
                continue
            name = fields[3]
            if name.upper() not in ('MD_SMEMINFO.BIN', 'MD_SHRDIMEM.BIN'):
                continue
            start = int(fields[1], 16)
            size = int(fields[2], 10)
            segment = dump_dir / name
            if not segment.is_file() or segment.stat().st_size < size:
                raise ValueError(f'Invalid minidump segment: {segment}')
            segments[name.upper()] = (segment, start, start + size)

    for name in ('MD_SMEMINFO.BIN', 'MD_SHRDIMEM.BIN'):
        if name not in segments:
            raise ValueError(f'Missing minidump segment: {name}')
        segment, start, end = segments[name]
        command.extend(['--ram-file', str(segment), f'0x{start:016x}', f'0x{end:016x}'])

    return command