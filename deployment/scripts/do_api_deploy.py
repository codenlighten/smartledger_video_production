#!/usr/bin/env python3
"""
HunyuanVideo DigitalOcean API Automation Script
This script creates and manages GPU Droplets for HunyuanVideo using the DigitalOcean API
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Optional

class DigitalOceanAPI:
    """DigitalOcean API client for GPU Droplet management"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv('DIGITALOCEAN_TOKEN')
        if not self.api_token:
            raise ValueError("DigitalOcean API token required. Set DIGITALOCEAN_TOKEN env var.")
        
        self.base_url = "https://api.digitalocean.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json() if response.text else {}
        
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            sys.exit(1)
    
    def get_ssh_keys(self) -> List[Dict]:
        """Get all SSH keys in account"""
        result = self._request("GET", "account/keys")
        return result.get("ssh_keys", [])
    
    def get_regions(self) -> List[Dict]:
        """Get all available regions"""
        result = self._request("GET", "regions")
        return result.get("regions", [])
    
    def get_droplets(self) -> List[Dict]:
        """Get all droplets"""
        result = self._request("GET", "droplets")
        return result.get("droplets", [])
    
    def create_gpu_droplet(
        self,
        name: str,
        region: str = "tor1",
        size: str = "gpu-h100-1x80gb-20vcpu-240gb",
        image: str = "ubuntu-25-10-x64",
        ssh_keys: Optional[List[str]] = None,
        startup_script: Optional[str] = None,
        tags: Optional[List[str]] = None,
        enable_ipv6: bool = False,
        enable_monitoring: bool = True
    ) -> Dict:
        """Create a new GPU Droplet"""
        
        data = {
            "name": name,
            "region": region,
            "size": size,
            "image": image,
            "backups": False,
            "ipv6": enable_ipv6,
            "monitoring": enable_monitoring,
            "tags": tags or ["hunyuan-video", "gpu", "ml"],
        }
        
        if ssh_keys:
            data["ssh_keys"] = ssh_keys
        
        if startup_script:
            data["user_data"] = startup_script
        
        print(f"Creating GPU Droplet: {name}")
        print(f"Region: {region}, Size: {size}")
        
        result = self._request("POST", "droplets", data)
        droplet = result.get("droplet", {})
        droplet_id = droplet.get("id")
        
        print(f"Droplet created! ID: {droplet_id}")
        print("Waiting for droplet to become active...")
        
        # Wait for droplet to be active
        self._wait_for_droplet_active(droplet_id)
        
        # Get final droplet details
        return self.get_droplet(droplet_id)
    
    def get_droplet(self, droplet_id: int) -> Dict:
        """Get droplet details"""
        result = self._request("GET", f"droplets/{droplet_id}")
        return result.get("droplet", {})
    
    def _wait_for_droplet_active(self, droplet_id: int, timeout: int = 300):
        """Wait for droplet to become active"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            droplet = self.get_droplet(droplet_id)
            status = droplet.get("status")
            
            if status == "active":
                print("Droplet is now active!")
                return
            
            print(f"Status: {status}, waiting...")
            time.sleep(10)
        
        raise TimeoutError(f"Droplet did not become active within {timeout} seconds")
    
    def delete_droplet(self, droplet_id: int):
        """Delete a droplet"""
        print(f"Deleting droplet {droplet_id}...")
        self._request("DELETE", f"droplets/{droplet_id}")
        print("Droplet deleted!")
    
    def get_droplet_by_name(self, name: str) -> Optional[Dict]:
        """Find droplet by name"""
        droplets = self.get_droplets()
        for droplet in droplets:
            if droplet.get("name") == name:
                return droplet
        return None


def load_startup_script(script_path: str) -> str:
    """Load startup script from file"""
    if not os.path.exists(script_path):
        print(f"Warning: Startup script not found: {script_path}")
        return ""
    
    with open(script_path, 'r') as f:
        return f.read()


def create_hunyuan_droplet(
    api: DigitalOceanAPI,
    name: str,
    deployment_type: str = "docker",
    region: str = "tor1",
    gpu_type: str = "h100-1x",
    ssh_key_ids: Optional[List[str]] = None
) -> Dict:
    """
    Create a HunyuanVideo GPU Droplet
    
    Args:
        api: DigitalOcean API client
        name: Droplet name
        deployment_type: 'docker' or 'manual'
        region: Datacenter region
        gpu_type: 'h100-1x' or 'h100-8x'
        ssh_key_ids: List of SSH key IDs or fingerprints
    """
    
    # GPU size mapping
    size_map = {
        "h200-1x": "gpu-h200-1x141gb-24vcpu-240gb",
        "h200-8x": "gpu-h200-8x141gb-192vcpu-1920gb",
        "h100-1x": "gpu-h100-1x80gb-20vcpu-240gb",
        "h100-8x": "gpu-h100-8x80gb-160vcpu-1920gb",
        "l40s-1x": "gpu-l40s-1x48gb-8vcpu-64gb",
    }
    
    size = size_map.get(gpu_type)
    if not size:
        raise ValueError(f"Unknown GPU type: {gpu_type}")
    
    # Load appropriate startup script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if deployment_type == "docker":
        script_path = os.path.join(script_dir, "docker-deploy.sh")
    else:
        script_path = os.path.join(script_dir, "startup.sh")
    
    startup_script = load_startup_script(script_path)
    
    # Get SSH keys if not provided
    if not ssh_key_ids:
        ssh_keys = api.get_ssh_keys()
        if ssh_keys:
            print("Available SSH keys:")
            for i, key in enumerate(ssh_keys):
                print(f"  {i+1}. {key['name']} ({key['fingerprint']})")
            
            choice = input("\nSelect SSH key number (or press Enter for all): ").strip()
            if choice:
                ssh_key_ids = [ssh_keys[int(choice)-1]['id']]
            else:
                ssh_key_ids = [k['id'] for k in ssh_keys]
    
    # Create droplet
    droplet = api.create_gpu_droplet(
        name=name,
        region=region,
        size=size,
        ssh_keys=ssh_key_ids,
        startup_script=startup_script,
        tags=["hunyuan-video", f"gpu-{gpu_type}", deployment_type]
    )
    
    return droplet


def print_droplet_info(droplet: Dict):
    """Print droplet information"""
    print("\n" + "="*70)
    print("GPU DROPLET CREATED SUCCESSFULLY")
    print("="*70)
    print(f"Name:       {droplet['name']}")
    print(f"ID:         {droplet['id']}")
    print(f"Status:     {droplet['status']}")
    print(f"Region:     {droplet['region']['name']}")
    
    # Get IP addresses
    networks = droplet.get('networks', {})
    v4_networks = networks.get('v4', [])
    v6_networks = networks.get('v6', [])
    
    if v4_networks:
        public_ips = [n['ip_address'] for n in v4_networks if n['type'] == 'public']
        private_ips = [n['ip_address'] for n in v4_networks if n['type'] == 'private']
        
        if public_ips:
            print(f"Public IP:  {public_ips[0]}")
        if private_ips:
            print(f"Private IP: {private_ips[0]}")
    
    if v6_networks:
        print(f"IPv6:       {v6_networks[0]['ip_address']}")
    
    print(f"\nGPU:        {droplet['size']['slug']}")
    print(f"vCPUs:      {droplet['vcpus']}")
    print(f"Memory:     {droplet['memory']} MB")
    print(f"Disk:       {droplet['disk']} GB")
    
    # Cost per hour based on GPU type
    slug = droplet['size']['slug']
    if 'h200' in slug and '8x' in slug:
        cost_per_hour = 27.52
    elif 'h200' in slug:
        cost_per_hour = 3.44
    elif 'h100' in slug and '8x' in slug:
        cost_per_hour = 23.92
    elif 'h100' in slug:
        cost_per_hour = 3.39
    elif 'l40s' in slug:
        cost_per_hour = 1.57
    else:
        cost_per_hour = 0.0
    print(f"\nCost:       ${cost_per_hour}/hour (${cost_per_hour * 730:.2f}/month)")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    
    if v4_networks and public_ips:
        ip = public_ips[0]
        print(f"\n1. SSH into droplet:")
        print(f"   ssh root@{ip}")
        print(f"\n2. Check setup progress:")
        print(f"   tail -f /var/log/hunyuan-video-setup.log")
        print(f"\n3. Download models (after setup completes):")
        print(f"   bash /opt/hunyuan-video/download_models.sh")
        print(f"\n4. Access Gradio interface (after models downloaded):")
        print(f"   http://{ip}:7860")
    
    print("\n" + "="*70)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="HunyuanVideo DigitalOcean GPU Droplet Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create H200 x1 droplet with Docker (RECOMMENDED)
  python do_api_deploy.py create --name my-hunyuan --gpu h200-1x --deployment docker
  
  # Create H100 x1 droplet (budget option)
  python do_api_deploy.py create --name my-hunyuan --gpu h100-1x --deployment docker
  
  # Create H200 x8 droplet for production
  python do_api_deploy.py create --name my-hunyuan-8gpu --gpu h200-8x --deployment manual
  
  # List all droplets
  python do_api_deploy.py list
  
  # Delete a droplet
  python do_api_deploy.py delete --name my-hunyuan
  
Environment:
  DIGITALOCEAN_TOKEN - Your DigitalOcean API token (required)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new GPU droplet')
    create_parser.add_argument('--name', required=True, help='Droplet name')
    create_parser.add_argument('--gpu', choices=['h200-1x', 'h200-8x', 'h100-1x', 'h100-8x', 'l40s-1x'], 
                              default='h200-1x',
                              help='GPU type (default: h200-1x - recommended)')
    create_parser.add_argument('--deployment', choices=['docker', 'manual'], default='docker',
                              help='Deployment type (default: docker)')
    create_parser.add_argument('--region', default='tor1',
                              help='Region code (default: tor1)')
    create_parser.add_argument('--ssh-keys', nargs='+',
                              help='SSH key IDs or fingerprints')
    
    # List command
    subparsers.add_parser('list', help='List all droplets')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a droplet')
    delete_parser.add_argument('--name', help='Droplet name')
    delete_parser.add_argument('--id', type=int, help='Droplet ID')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get droplet info')
    info_parser.add_argument('--name', help='Droplet name')
    info_parser.add_argument('--id', type=int, help='Droplet ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize API
    try:
        api = DigitalOceanAPI()
    except ValueError as e:
        print(f"Error: {e}")
        print("\nSet your DigitalOcean API token:")
        print("  export DIGITALOCEAN_TOKEN='your-token-here'")
        sys.exit(1)
    
    # Execute command
    if args.command == 'create':
        droplet = create_hunyuan_droplet(
            api=api,
            name=args.name,
            deployment_type=args.deployment,
            region=args.region,
            gpu_type=args.gpu,
            ssh_key_ids=args.ssh_keys
        )
        print_droplet_info(droplet)
    
    elif args.command == 'list':
        droplets = api.get_droplets()
        print(f"\nFound {len(droplets)} droplet(s):\n")
        for d in droplets:
            tags = ', '.join(d.get('tags', []))
            print(f"  {d['name']:<30} [{d['id']}]")
            print(f"    Status: {d['status']:<10} Region: {d['region']['slug']:<10}")
            if tags:
                print(f"    Tags: {tags}")
            
            v4 = d.get('networks', {}).get('v4', [])
            if v4:
                public = [n['ip_address'] for n in v4 if n['type'] == 'public']
                if public:
                    print(f"    IP: {public[0]}")
            print()
    
    elif args.command == 'delete':
        if args.id:
            api.delete_droplet(args.id)
        elif args.name:
            droplet = api.get_droplet_by_name(args.name)
            if droplet:
                api.delete_droplet(droplet['id'])
            else:
                print(f"Droplet not found: {args.name}")
        else:
            print("Error: Specify --name or --id")
            sys.exit(1)
    
    elif args.command == 'info':
        if args.id:
            droplet = api.get_droplet(args.id)
        elif args.name:
            droplet = api.get_droplet_by_name(args.name)
        else:
            print("Error: Specify --name or --id")
            sys.exit(1)
        
        if droplet:
            print_droplet_info(droplet)
        else:
            print("Droplet not found")


if __name__ == '__main__':
    main()
