import { useFetch, useWindowScroll } from '@mantine/hooks';
import { useParams } from 'react-router-dom'
import { Stack, Text, Loader, Center, ActionIcon, Title, Group, Menu, Button, rem } from '@mantine/core';
import { IconChevronUp, IconDownload, IconLanguage, IconWorld } from '@tabler/icons-react';
import classes from '@/pages/Chapter.module.css'
import { NavBar } from '@/components/NavBar/NavBar';
import { useContext } from 'react';
import { SettingsContext } from '@/contexts/SettingsContext';


const pages = (data: string[]) => {
    if (data instanceof Array) {
        return data.map((pagePath: string) => (<img src={pagePath} key={pagePath} className={classes.images}/>))
    }
    else {
        return (<Text c="red">Error</Text>)
    }
}

const Chapter = () => {
    const {toonkorId, chapter, choice} = useParams();
    const {data, loading, error} = useFetch<string[]>(`/api/chapter?toonkor_id=/${toonkorId}&chapter=${chapter}&choice=${choice}`);
    const [scroll, scrollTo] = useWindowScroll();
    const {toonkorUrl} = useContext(SettingsContext);

    const openToonkorURL = (chapterId: string | undefined) => {
        if (toonkorId) {
          const chapterUrl = toonkorUrl + chapterId;
          window.open(chapterUrl);
        }
      };
    
      const openLocalURL = (chapterIndex: string | undefined, choice: 'downloaded' | 'translated') => {
        if (toonkorId) {
          const chapterUrl = `/manhwa/${toonkorId}/${chapterIndex}/${choice}`;
          window.open(chapterUrl);
        }
      };

    const otherChapter = () => (
      <Group justify='space-between'>
      {['Prev', 'Next'].map((position) => <Menu trigger="hover" position="bottom">
          <Menu.Target>
            <Button
              variant="gradient"
              size="lg"
              aria-label="Gradient action icon"
              gradient={{ from: 'blue', to: 'cyan', deg: 90 }}
            >
              {position}
            </Button>
          </Menu.Target>
          <Menu.Dropdown>
            <Menu.Item
              onClick={() => openToonkorURL(chapter)}
              leftSection={<IconWorld style={{ width: rem(14), height: rem(14) }} />}
            >
              Toonkor URL
            </Menu.Item>
            <Menu.Item
              onClick={() => openLocalURL(chapter, 'downloaded')}
              leftSection={<IconDownload style={{ width: rem(14), height: rem(14) }} />}
            >
              Download URL
            </Menu.Item>
            <Menu.Item
              onClick={() => openLocalURL(chapter, 'translated')}
              leftSection={<IconLanguage style={{ width: rem(14), height: rem(14) }} />}
            >
              Translation URL
            </Menu.Item>
          </Menu.Dropdown>
        </Menu>
      )}
    </Group>
    )

    return (
        <>
        <NavBar showSearchBar={false}/>
        <Title mx="auto">Chapter {chapter}</Title>
        <Stack mx="auto" gap={0}>
          {otherChapter()}
            {loading && <Center><Loader color="blue" /></Center>}
            {error && <Text c="red">{error.message}</Text>}
            {data && pages(data)}
            {scroll.y !== 0 && <ActionIcon size="lg" radius="lg" className={classes.anchor} onClick={() => scrollTo({ y: 0 })}>
                <IconChevronUp />
            </ActionIcon>}
        {otherChapter()}
        </Stack>
        </>
    )
}

export default Chapter