import { useState, useEffect } from 'react';
import { ManhwaCardsGrid } from '@/components/ManhwaCardsGrid/ManhwaCardsGrid';
import ManhwaData from '@/types/manhwaData';
import { useFetch } from '@mantine/hooks';
import { LoadingOverlay, Text } from '@mantine/core';
import { NavBar } from '@/components/NavBar/NavBar';


const Library = () => {
  // Fetching the data using useFetch
  const { data, loading, error } = useFetch<ManhwaData[]>(
    '/api/library'
  );
  const [manhwaList, setManhwaList] = useState<ManhwaData[]>([]);
  document.title = "Library";

  // Update manhwaList when data is fetched
  useEffect(() => {
    if (data) {
      setManhwaList(data);
    }
  }, [data]);

  // Handling search input changes
  const onSearchChange = (value: string) => {
    if (data) {
      const filtered = data.filter((manhwa) =>
        manhwa.title.toLowerCase().includes(value.toLowerCase())
      );
      setManhwaList(filtered);
    }
  };

  return (
    <>
      <NavBar
        onSearchChange={onSearchChange}
        showSearchBar={true}
      />
      <LoadingOverlay visible={loading} />
      {error && <Text color="red">{error.message}</Text>}
      {manhwaList && <ManhwaCardsGrid data={manhwaList} />}
    </>
  );
};

export default Library;
