import cx from 'clsx';
import { useState, useEffect, useContext } from 'react';
import { Table, Checkbox, ScrollArea, Group, Text, rem, Button, Menu, ActionIcon, Loader, Grid, Flex, Tooltip } from '@mantine/core';
import classes from './ChaptersTable.module.css';
import ChapterData from '@/types/chapterData';
import { IconDownload, IconFilter, IconLanguage, IconLink, IconTrash, IconWorld } from '@tabler/icons-react';
import { SettingsContext } from '@/contexts/SettingsContext';

interface ChaptersTableProps {
  slug: string | undefined;
  chapters: ChapterData[];
}

const ChaptersTable = ({ slug, chapters = [] }: ChaptersTableProps) => {
  const [selection, setSelection] = useState<ChapterData[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const {toonkorUrl} = useContext(SettingsContext); 

  useEffect(() => {
    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/download_translate/${slug}/`);
    setSocket(ws);

    ws.onopen = () => console.log("Connected to Django server");
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data).progress;
      const progress = Math.floor(data.current / data.total * 100);
      console.log(progress);
    };
    ws.onerror = (e) => console.error('WebSocket error:', e);
    ws.onclose = (e) => {
      if (e.wasClean) {
        console.log('WebSocket closed cleanly');
      } else {
        console.error('WebSocket closed unexpectedly:', e);
      }
    };

    return () => {
      ws.close();
    };
  }, [slug]);

  const toggleRow = (chapter: ChapterData) => {
    setSelection((current) =>
      current.includes(chapter)
        ? current.filter((item) => item.index !== chapter.index)
        : [...current, chapter]
    );
  };

  const toggleAll = () => {
    setSelection((current) =>
      current.length === chapters.length ? [] : [...chapters]
    );
  };

  const download = () => {
    if (socket) {
      const msg = {
        task: 'download',
        slug: slug,
        chapters: selection.map((chapter) => chapter.index),
      };
      socket.send(JSON.stringify(msg));
    }
  };

  const downloadTranslate = () => {
    if (socket) {
      const updatedChapters = chapters.map((chapter) =>
        selection.includes(chapter) ? { ...chapter, status: 'translating' } : chapter
      );
      setSelection(updatedChapters.filter((chapter) => chapter.status === 'translating'));

      const msg = {
        task: 'download_translate',
        slug: slug,
        chapters: selection.map((chapter) => chapter.index),
      };
      socket.send(JSON.stringify(msg));
    }
  };

  const openToonkorURL = (chapterIndex: string) => {
    if (slug) {
      const chapterSlug = slug.replaceAll('-', '_');
      const chapterUrl = `${toonkorUrl}/${chapterSlug}_${chapterIndex}화.html`;
      window.open(chapterUrl, "_blank", "noreferrer");
    }
  };

  const openDownloadURL = () => {
    // Implement the actual URL here
  };

  const openTranslationURL = () => {
    // Implement the actual URL here
  };

  const rows = chapters.map((chapter) => {
    const selected = selection.some((item) => item.index === chapter.index);
    return (
      <Table.Tr key={chapter.index} className={cx({ [classes.rowSelected]: selected })}>
        <Table.Td>
          <Checkbox checked={selected} disabled={chapter.status === 'translating'} onChange={() => toggleRow(chapter)} />
        </Table.Td>
        <Table.Td>
          <Group gap="sm">
            <Text size="sm" fw={500}>
              {chapter.index}
            </Text>
          </Group>
        </Table.Td>
        <Table.Td>{chapter.date_upload}</Table.Td>
        <Table.Td>
          {chapter.status === 'translating' && <Loader color='cyan' />}
          {chapter.status}
        </Table.Td>
        <Table.Td>
          <Menu trigger="hover" position='right'>
            <Menu.Target>
              <ActionIcon
                variant="gradient"
                size="lg"
                aria-label="Gradient action icon"
                gradient={{ from: 'blue', to: 'cyan', deg: 90 }}
              >
                <IconLink />
              </ActionIcon>
            </Menu.Target>
            <Menu.Dropdown>
              <Menu.Item onClick={() => openToonkorURL(chapter.index)} leftSection={<IconWorld style={{ width: rem(14), height: rem(14) }} />}>
                Toonkor URL
              </Menu.Item>
              <Menu.Item onClick={openDownloadURL} leftSection={<IconDownload style={{ width: rem(14), height: rem(14) }} />}>
                Download URL
              </Menu.Item>
              <Menu.Item onClick={openTranslationURL} leftSection={<IconLanguage style={{ width: rem(14), height: rem(14) }} />}>
                Translation URL
              </Menu.Item>
            </Menu.Dropdown>
          </Menu>
        </Table.Td>
      </Table.Tr>
    );
  });

  return (
    <div>
      <Group justify='end'>
        <Tooltip label="Download">
        <ActionIcon variant='default'>
          <IconDownload />
        </ActionIcon>
        </Tooltip>
        <Tooltip label="Download & Translate">
        <ActionIcon variant='default'>
          <IconLanguage />
        </ActionIcon>
        </Tooltip>
        <Tooltip label="Delete">
        <ActionIcon variant='default'>
          <IconTrash />
        </ActionIcon>
        </Tooltip>
        <Tooltip label="Filter">
        <ActionIcon variant='default'>
          <IconFilter />
        </ActionIcon>
        </Tooltip>
      </Group>
      <ScrollArea>
        <Table highlightOnHover miw={800} verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th style={{ width: rem(40) }}>
                <Checkbox
                  onChange={toggleAll}
                  checked={selection.length === chapters.length}
                  indeterminate={selection.length > 0 && selection.length !== chapters.length}
                />
              </Table.Th>
              <Table.Th>Chapter</Table.Th>
              <Table.Th>Date</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Links</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>{rows}</Table.Tbody>
        </Table>
      </ScrollArea>
    </div>
  );
};

export default ChaptersTable;
