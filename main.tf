provider "google" {
  project     = "operations-342911"
  region      = "us-west2"
  zone        = "us-west2-a"
}

# Main VPC
resource "google_compute_network" "vpc_network" {
  name                    = "vpc-terraform"
  auto_create_subnetworks = false
}

# Public Subnet
resource "google_compute_subnetwork" "public" {
  name          = "public-aswin-terraform"
  ip_cidr_range = "10.0.0.0/24"
  region        = "us-west2"
  network       = google_compute_network.vpc_network.id
}

# Private Subnet
resource "google_compute_subnetwork" "private" {
  name          = "private-aswin-terrafrom"
  ip_cidr_range = "10.0.1.0/24"
  region        = "us-west2"
  network       = google_compute_network.vpc_network.id
}

# Cloud Router
resource "google_compute_router" "router" {
  name    = "router"
  network = google_compute_network.vpc_network.id
  bgp {
    asn            = 64514
    advertise_mode = "CUSTOM"
  }
}

# NAT Gateway
resource "google_compute_router_nat" "nat" {
  name                               = "nat"
  router                             = google_compute_router.router.name
  region                             = google_compute_router.router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"

  subnetwork {
    name                    = "private"
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
}