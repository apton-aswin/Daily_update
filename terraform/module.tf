module "vpc" {
    source  = "terraform-google-modules/network/google//modules/vpc"
    #version = "~>  5.0.0."

    project_id   = "operations-342911"
    network_name = "terraform-vpc"

    shared_vpc_host = false
}