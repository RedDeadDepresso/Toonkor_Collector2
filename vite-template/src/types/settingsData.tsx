import { MantineColorScheme } from '@mantine/core';
import readData from './readData';

interface SettingsData {
  colorScheme: MantineColorScheme;
  displayEnglish: boolean;
  autoFetchToonkorUrl: boolean;
  toonkorUrl: string;
  read: readData;
  setToonkorUrl: (value: string) => void;
  setAutoFetchToonkorUrl: (value: boolean) => void;
  setColorScheme: (value: MantineColorScheme) => void;
  setDisplayEnglish: (value: boolean) => void;
  setRead: (value: readData) => void
}

export default SettingsData;
