import { useFetch } from '@mantine/hooks';
import { useParams } from 'react-router-dom'
import { Stack, Text, Loader, Center } from '@mantine/core';


const pages = (data: string[]) => {
    console.log(data);
    if (data instanceof Array) {
        return data.map((pagePath: string) => (<img src={pagePath} key={pagePath}/>))
    }
    else {
        return (<Text c="red">Error</Text>)
    }
}

const Chapter = () => {
    const {toonkorId, chapter, choice} = useParams();
    const {data, loading, error} = useFetch<string[]>(`/api/chapter?toonkor_id=/${toonkorId}&chapter=${chapter}&choice=${choice}`);

    return (
        <Stack mx="auto" gap={0}>
            {loading && <Center><Loader color="blue" /></Center>}
            {error && <Text c="red">{error.message}</Text>}
            {data && pages(data)}
        </Stack>
    )
}

export default Chapter