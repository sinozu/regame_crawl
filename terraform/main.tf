provider "google" {
    credentials = file("CREDENTIALS_FILE.json")
    project     = "${var.project_name}"
    region      = "asia-northeast1"
}

data "archive_file" "function_zip" {
    type        = "zip"
    source_dir  = "${path.module}/../crawl"
    output_path = "${path.module}/files/functions.zip"
}

resource "google_storage_bucket" "regame_crawl_functions_bucket" {
    name          = "${var.project_name}-scheduler-bucket"
    project       = "${var.project_name}"
    location      = "asia"
    force_destroy = true
}

resource "google_storage_bucket_object" "functions_zip" {
    name   = "functions.zip"
    bucket = "${google_storage_bucket.regame_crawl_functions_bucket.name}"
    source = "${path.module}/files/functions.zip"
}


resource "google_pubsub_topic" "regame_crawl_pubsub" {
    name    = "regame-crawl-pubsub"
    project = "${var.project_name}"
}

resource "google_cloudfunctions_function" "regame_crawl" {
  name        = "RegameCrawl"
  project     = "${var.project_name}"
  region      = "asia-northeast1"
  runtime     = "python38"
  entry_point = "main"
  timeout     = 300

  source_archive_bucket = "${google_storage_bucket.regame_crawl_functions_bucket.name}"
  source_archive_object = "${google_storage_bucket_object.functions_zip.name}"

  environment_variables = {
      NOTION_API_KEY     = "${var.notion_api_key}"
      NOTION_DATABASE_ID = "${var.notion_database_id}"
      NOTION_VERSION     = "${var.notion_version}"
  }

  event_trigger {
    event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
    resource   = "${google_pubsub_topic.regame_crawl_pubsub.name}"
  }
}

resource "google_cloud_scheduler_job" "regame_crawl_scheduler" {
    name        = "regame-crawl-daily"
    project     = "${var.project_name}"
    schedule    = "0 8 * * *"
    description = "Crawl Real Escape Game Info"
    time_zone   = "Asia/Tokyo"

    pubsub_target {
        topic_name = "${google_pubsub_topic.regame_crawl_pubsub.id}"
        data       = base64encode("test")
    }
}