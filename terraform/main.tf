provider "google" {
  project = var.project_name
  region  = "asia-northeast1"
}

terraform {
  backend "gcs" {
    bucket  = "regame-crawl-terraform-bucket"
  }
}

data "archive_file" "function_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../crawl"
  output_path = "${path.module}/files/functions.zip"
}

resource "google_storage_bucket" "regame_crawl_functions_bucket" {
  name          = "${var.project_name}-scheduler-bucket"
  project       = var.project_name
  location      = "asia"
  force_destroy = true
}

resource "google_storage_bucket_object" "functions_zip" {
  name   = "functions.zip"
  bucket = google_storage_bucket.regame_crawl_functions_bucket.name
  source = "${path.module}/files/functions.zip"
}


resource "google_pubsub_topic" "regame_crawl_pubsub" {
  name    = "regame-crawl-pubsub"
  project = var.project_name
}

resource "google_cloudfunctions_function" "regame_crawl" {
  name        = "RegameCrawl"
  project     = var.project_name
  region      = "asia-northeast1"
  runtime     = "python38"
  entry_point = "main"
  timeout     = 300

  source_archive_bucket = google_storage_bucket.regame_crawl_functions_bucket.name
  source_archive_object = google_storage_bucket_object.functions_zip.name

  environment_variables = {
    NOTION_API_KEY     = "${var.notion_api_key}"
    NOTION_DATABASE_ID = "${var.notion_database_id}"
    NOTION_VERSION     = "${var.notion_version}"
  }

  event_trigger {
    event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
    resource   = google_pubsub_topic.regame_crawl_pubsub.name
  }
}

resource "google_cloud_scheduler_job" "regame_crawl_scheduler" {
  name        = "regame-crawl-daily"
  project     = var.project_name
  schedule    = "0 8 * * *"
  description = "Crawl Real Escape Game Info"
  time_zone   = "Asia/Tokyo"

  pubsub_target {
    topic_name = google_pubsub_topic.regame_crawl_pubsub.id
    data       = base64encode("test")
  }
}

## tfstate
resource "google_storage_bucket" "regame-crawl-terraform-state-store" {
  name     = "regame-crawl-terraform-bucket"
  location = "us-west1"
  storage_class = "REGIONAL"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      num_newer_versions = 5
    }
  }
}

resource "google_monitoring_notification_channel" "basic" {
  display_name = "Error Notification To Email"
  type         = "email"
  labels = {
    email_address = "${var.error_notify_email}"
  }
}
