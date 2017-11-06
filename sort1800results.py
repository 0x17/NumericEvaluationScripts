outstr = ''
with open('GA4Results_Ref1800secs_unsorted.txt', 'r') as fp2:
    lines2 = fp2.readlines()
    with open('j120_60secs/GA0Results.txt', 'r') as fp:
        for line in fp.readlines():
            parts = line.split(';')
            instance_name = parts[0]
            for line2 in lines2:
                parts2 = line2.split(';')
                if parts2[0] == instance_name:
                    outstr += instance_name+';'+parts2[1]
with open('GA4Results_Ref1800secs_SORTED.txt', 'w') as fpw:
    fpw.write(outstr)