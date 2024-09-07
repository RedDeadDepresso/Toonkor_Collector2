import React, { createContext, useEffect } from 'react';
import { useLocalStorage } from '@mantine/hooks';
import SettingsData from '@/types/settingsData';
import { useMantineColorScheme } from '@mantine/core';

interface childrenProps {
    children: React.ReactNode
}

export const SettingsContext = createContext<SettingsData>({} as SettingsData);

export const SettingsProvider = ({ children }: childrenProps) => {
    const [displayEnglish, setDisplayEnglish] = useLocalStorage({
        key: 'display_english',
        defaultValue: true,
    });
    const { colorScheme, setColorScheme } = useMantineColorScheme();
    const [autoFetchToonkorUrl, setAutoFetchToonkorUrl] = useLocalStorage({
        key: 'auto_fetch_toonkor_url',
        defaultValue: false,
    });
    const [toonkorUrl, setToonkorUrl] = useLocalStorage({ key: 'toonkor_url', defaultValue: 'https://toonkor434.com' });

    const fetchToonkorUrl = async () => {
      try {
          const response = await fetch('/api/fetch_toonkor_url');
          if (!response.ok) {
              throw new Error(`Response status: ${response.status}`);
          }
          const json = await response.json();
          if (!json.error) {
            setToonkorUrl(json.url);
          }
          console.log(json);
      } catch (error: any) {
          console.error(error.message);
      }
    };

    useEffect(() => {
        if (!autoFetchToonkorUrl) {
            fetch('/api/set_toonkor_url', {
                method: "POST",
                body: JSON.stringify({url: toonkorUrl})
            }).then(() => console.log("URL set on server"))
        }
    }, [])

    useEffect(() => {
        if (autoFetchToonkorUrl || !toonkorUrl) {
            fetchToonkorUrl();
        }
    }, [autoFetchToonkorUrl, toonkorUrl]);


    return (
        <SettingsContext.Provider value={{
            displayEnglish,
            setDisplayEnglish,
            colorScheme,
            setColorScheme,
            autoFetchToonkorUrl,
            setAutoFetchToonkorUrl,
            toonkorUrl,
            setToonkorUrl
        }}>
            {children}
        </SettingsContext.Provider>
    );
};
