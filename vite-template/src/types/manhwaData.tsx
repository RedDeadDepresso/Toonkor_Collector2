import ChapterData from "./chapterData"

interface ManhwaData {
    title: string 
    description: string
  
    en_title: string
    en_description: string

    thumbnail: string
    chapters: Array<ChapterData>
    in_library: boolean

    mangadex_url: string
    toonkor_url: string
    slug: string
}

export default ManhwaData