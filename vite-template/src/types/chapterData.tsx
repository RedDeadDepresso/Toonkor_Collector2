interface ChapterData {
    index: string
    date_upload: string
    toonkor_id: string

    download_status: "NOT_READY" | "LOADING" | "READY"
    translation_status: "NOT_READY" | "LOADING" | "READY"
}

export default ChapterData;