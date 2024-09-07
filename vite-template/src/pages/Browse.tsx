import { useState } from 'react';
import { ManhwaCardsGrid } from '@/components/ManhwaCardsGrid/ManhwaCardsGrid';
import ManhwaData from '@/types/manhwaData';
import { Text } from '@mantine/core';
import { NavBar } from '@/components/NavBar/NavBar';

const Browse = () => {
  const [firstRender, setFirstRender] = useState<boolean>(true);
  const [manhwaList, setManhwaList] = useState<ManhwaData[]>([]);
  const [errorMessage, setErrorMessage] = useState<string>('');
  document.title = "Browse";

  const onSearchChange = async (searchQuery: string) => {
    firstRender && setFirstRender(false);
    const url = `/api/browse/search?query=${searchQuery}`;
    try {
      const response = await fetch(url);
      if (!response.ok) {
        setErrorMessage(`Response status: ${response.status}`);
      }
      const json = await response.json();
      setManhwaList(json);
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage('An unknown error occurred.');
      }
    }
  };

  return (
    <>
      <NavBar onSearchChange={onSearchChange} showSearchBar={true} />
      {firstRender && <Text>Search something...</Text>}
      {manhwaList && <ManhwaCardsGrid data={manhwaList} />}
      {errorMessage && <Text color="red">{errorMessage}</Text>}
      {!firstRender && !manhwaList.length && <Text>No results were found</Text>}
    </>
  );
};

export default Browse;
