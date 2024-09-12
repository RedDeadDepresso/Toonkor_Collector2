import { SettingsContext } from "@/contexts/SettingsContext"
import ChapterData from "@/types/chapterData"
import { FloatingPosition, Menu, rem } from "@mantine/core"
import { IconDownload, IconLanguage, IconWorld } from "@tabler/icons-react"
import { ReactNode, useContext } from "react"
import { useNavigate } from "react-router-dom"


interface MenuLinkProps {
    children: ReactNode
    chapter: ChapterData;
    position: FloatingPosition | undefined;
    newTab?: boolean;
}

const MenuLink = ({children, chapter, position, newTab=false}: MenuLinkProps) => {
    const {toonkorUrl, read, setRead} = useContext(SettingsContext);
    const navigate = useNavigate()

    const openToonkorURL = (chapterId: string) => {
        const chapterUrl = toonkorUrl + chapterId;
        setRead({ ...read, [chapterId]: true });
        if (newTab) {
            window.open(chapterUrl, '_blank', 'noreferrer');
        }
        else {
          window.location.href = chapterUrl;
        }
    };
    
    const openLocalURL = (chapterId: string, choice: 'downloaded' | 'translated') => {
        const chapterUrl = `/chapter${chapterId}/${choice}`;
        setRead({ ...read, [chapterId]: true });
        if (newTab) {
            window.open(chapterUrl, '_blank', 'noreferrer');
        }
        else {
          navigate(chapterUrl);
        }
    };

    return (
        <Menu trigger="click-hover" position={position}>
        <Menu.Target>
            {children}
        </Menu.Target>
        <Menu.Dropdown>
          <Menu.Item
            onClick={(event) => {event.stopPropagation(); openToonkorURL(chapter.toonkor_id)}}
            leftSection={<IconWorld style={{ width: rem(14), height: rem(14) }} />}
          >
            Toonkor URL
          </Menu.Item>
          <Menu.Item
            disabled={chapter.status === 'On Toonkor' || chapter.status === 'Downloading'}
            onClick={(event) => {event.stopPropagation(); openLocalURL(chapter.toonkor_id, 'downloaded')}}
            leftSection={<IconDownload style={{ width: rem(14), height: rem(14) }} />}
          >
            Download URL
          </Menu.Item>
          <Menu.Item
            disabled={chapter.status !== 'Translated'}
            onClick={(event) => {event.stopPropagation(); openLocalURL(chapter.toonkor_id, 'translated')}}
            leftSection={<IconLanguage style={{ width: rem(14), height: rem(14) }} />}
          >
            Translation URL
          </Menu.Item>
        </Menu.Dropdown>
      </Menu>
    )
}


export default MenuLink;