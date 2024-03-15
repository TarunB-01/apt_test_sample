import nmap

def perform_scan(target):
    nm = nmap.PortScanner()
    nm.scan(hosts=target, arguments='-sS -Pn -p 1-1000')

    return nm

def generate_report(scan_results, output_file):
    with open(output_file, 'w') as f:
        f.write("Nmap Scan Report:\n")
        for host in scan_results.all_hosts():
            f.write(f"\nHost: {host}\n")
            f.write("State: {}\n".format(scan_results[host].state()))
            for proto in scan_results[host].all_protocols():
                f.write("-----------------------------\n")
                f.write("Protocol: {}\n".format(proto))
                ports = scan_results[host][proto].keys()
                for port in ports:
                    f.write("Port: {} \tState: {}\n".format(port, scan_results[host][proto][port]['state']))

if __name__ == "__main__":
    target = input("Enter target IP or hostname: ")
    output_file = input("Enter output file name: ")
    
    scan_results = perform_scan(target)
    generate_report(scan_results, output_file)
    print(f"Scan results have been saved to {output_file}")
