module "vpc" {
    source  = "/home/aswin/devops/Daily_update/work/terraform"
    #version = "~>  5.0.0."

    project_id   = "operations-342911"
    network_name = "terraform-vpc"

    shared_vpc_host = false
}