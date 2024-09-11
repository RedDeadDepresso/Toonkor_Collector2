import cx from 'clsx';
import { useState, useEffect, useContext } from 'react';
import {
  Table,
  Checkbox,
  ScrollArea,
  Group,
  Text,
  rem,
  Button,
  Menu,
  ActionIcon,
  Loader,
  Tooltip,
  Popover,
} from '@mantine/core';
import classes from './ChaptersTable.module.css';
import ChapterData from '@/types/chapterData';
import {
  IconDownload,
  IconFilter,
  IconLanguage,
  IconLink,
  IconTrash,
  IconWorld,
} from '@tabler/icons-react';
import { SettingsContext } from '@/contexts/SettingsContext';

interface ChaptersTableProps {
  toonkorId: string | undefined;
  chapterDataList: ChapterData[];
}

const ChaptersTable = ({ toonkorId, chapterDataList = [] }: ChaptersTableProps) => {
  const [chapters, setChapters] = useState<ChapterData[]>(chapterDataList);
  const [selection, setSelection] = useState<ChapterData[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const { toonkorUrl } = useContext(SettingsContext);
  const [filters, setFilters] = useState({
    downloaded: false,
    translated: false
  });
  
  useEffect(() => {
    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/download_translate/${toonkorId}/`);
    setSocket(ws);

    ws.onopen = () => console.log('Connected to Django server');
    ws.onmessage = handleWebSocketMessage;
    ws.onerror = (e) => console.error('WebSocket error:', e);
    ws.onclose = (e) => {
      console.log(e.wasClean ? 'WebSocket closed cleanly' : 'WebSocket closed unexpectedly:', e);
    };

    return () => ws.close();
  }, [toonkorId]);

  useEffect(() => {
    applyFilters();
  }, [filters]);

  const handleWebSocketMessage = (e: MessageEvent) => {
    const { task, current_chapter, progress } = JSON.parse(e.data);
    console.log(JSON.parse(e.data));
    
    // Update chapters array immutably
    setChapters(prevChapters => {
      return prevChapters.map(chapter => {
        if (chapter.index === current_chapter) {
          // Ensure the chapter's status is correctly updated based on the task
          if (task === 'download') return { ...chapter, status: 'Downloaded' };
          if (task === 'download_translate') return { ...chapter, status: 'Translated' };
        }
        return chapter; // Return the chapter as it is if not updated
      });
    });
  };  

  const applyFilters = () => {
    if (filters.downloaded) {
      setChapters(chapterDataList.filter(chapter => chapter.status === 'Downloaded' || chapter.status === 'Translated'));
    } else if (filters.translated) {
      setChapters(chapterDataList.filter(chapter => chapter.status === 'Translated'));
    } else {
      setChapters(chapterDataList);
    }
  };

  const toggleRow = (chapter: ChapterData) => {
    setSelection(prevSelection =>
      prevSelection.includes(chapter)
        ? prevSelection.filter(item => item.index !== chapter.index)
        : [...prevSelection, chapter]
    );
  };

  const toggleAll = () => {
    setSelection(selection.length === chapters.length ? [] : [...chapters]);
  };

  const download = () => {
    const updatedChapters = chapterDataList.map((chapter) =>
      selection.some((selectedChapter) => selectedChapter.index === chapter.index)
        ? { ...chapter, status: 'Downloading' }
        : chapter
    );
    setChapters(updatedChapters);

    if (socket) {
      socket.send(JSON.stringify({
        task: 'download',
        toonkor_id: `/${toonkorId}`,
        chapters: selection,
      }));
    }
  };

  const downloadTranslate = () => {
    const updatedChapters = chapterDataList.map((chapter) =>
      selection.some((selectedChapter) => selectedChapter.index === chapter.index)
        ? { ...chapter, status: 'Translating' }
        : chapter
    );
    setChapters(updatedChapters);

    if (socket) {
      socket.send(JSON.stringify({
        task: 'download_translate',
        toonkor_id: `/${toonkorId}`,
        chapters: selection,
      }));
    }
  };

  const remove = () => {};

  const openToonkorURL = (chapterId: string) => {
    if (toonkorId) {
      const chapterUrl = toonkorUrl + chapterId;
      window.open(chapterUrl, '_blank', 'noreferrer');
    }
  };

  const openLocalURL = (chapterIndex: string, choice: 'downloaded' | 'translated') => {
    if (toonkorId) {
      const chapterUrl = `/manhwa/${toonkorId}/${chapterIndex}/${choice}`;
      window.open(chapterUrl, '_blank', 'noreferrer');
    }
  };

  const rows = [];
  for (let i = chapters.length - 1; i >= 0; i--) {
    const chapter = chapters[i];
    const selected = selection.some((item) => item.index === chapter.index);
  
    rows.push(
      <Table.Tr
        key={chapter.index}
        className={cx({ [classes.rowSelected]: selected })}
        onClick={() => {toggleRow(chapter)}}
      >
        <Table.Td>
          <Checkbox
            checked={selected}
            disabled={chapter.status === 'Translating'}
            onChange={() => toggleRow(chapter)}
          />
        </Table.Td>
        <Table.Td>
          <Group gap="sm">
            <Text size="sm" fw={500}>
              {chapter.index + 1}
            </Text>
          </Group>
        </Table.Td>
        <Table.Td>{chapter.date_upload}</Table.Td>
        <Table.Td>
          <span>
            {chapter.status === 'Downloading' && (
              <Loader size="sm" color="orange" />
            )}
            {chapter.status === 'Translating' && (
              <Loader size="sm" color="cyan" />
            )}
            {chapter.status}
          </span>
        </Table.Td>
        <Table.Td>
          <Menu trigger="hover" position="right">
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
              <Menu.Item
                onClick={() => openToonkorURL(chapter.toonkor_id)}
                leftSection={<IconWorld style={{ width: rem(14), height: rem(14) }} />}
              >
                Toonkor URL
              </Menu.Item>
              <Menu.Item
                disabled={chapter.status === 'On Toonkor' || chapter.status === 'Downloading'}
                onClick={() => openLocalURL(chapter.index, 'downloaded')}
                leftSection={<IconDownload style={{ width: rem(14), height: rem(14) }} />}
              >
                Download URL
              </Menu.Item>
              <Menu.Item
                disabled={chapter.status !== 'Translated'}
                onClick={() => openLocalURL(chapter.index, 'translated')}
                leftSection={<IconLanguage style={{ width: rem(14), height: rem(14) }} />}
              >
                Translation URL
              </Menu.Item>
            </Menu.Dropdown>
          </Menu>
        </Table.Td>
      </Table.Tr>
    );
  }  

  return (
    <div>
      <Group justify="end">
        <Tooltip label="Download">
          <ActionIcon variant="default" onClick={download}>
            <IconDownload />
          </ActionIcon>
        </Tooltip>
        <Tooltip label="Download & Translate">
          <ActionIcon variant="default" onClick={downloadTranslate}>
            <IconLanguage />
          </ActionIcon>
        </Tooltip>
        <Tooltip label="Remove">
          <ActionIcon variant="default" onClick={remove}>
            <IconTrash />
          </ActionIcon>
        </Tooltip>
        <Popover width={300} trapFocus position="bottom" withArrow shadow="md">
          <Popover.Target>
            <Tooltip label="Filter">
              <ActionIcon variant="default">
                <IconFilter />
              </ActionIcon>
            </Tooltip>
          </Popover.Target>
          <Popover.Dropdown>
            <Checkbox
              label="Downloaded"
              checked={filters.downloaded}
              onChange={(event) => setFilters({ ...filters, downloaded: event.currentTarget.checked })}
            />
            <Checkbox
              label="Translated"
              checked={filters.translated}
              onChange={(event) => setFilters({ ...filters, translated: event.currentTarget.checked })}
            />
          </Popover.Dropdown>
        </Popover>
      </Group>
      <ScrollArea h={rem(750)}>
        <Table highlightOnHover verticalSpacing="sm" stickyHeader>
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
