'use client'
import { Search, CornerDownLeft } from '@geist-ui/icons'

import styles from './page.module.css'
import { Input, Button } from '@geist-ui/core'
import {useState} from "react";
import {Result} from "@/app/page";

interface SearchBarProps {
    results: Result[]
    setResult: (results: Result[]) => void
}

export default function SearchBar({results, setResult}: SearchBarProps) {

    // input state
    const [input, setInput] = useState<string>("")

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setInput(e.target.value)
    }

    const queryServer = () => {
        fetch(`/api/search?query=${input}`)
            .then(res => res.json())
            .then(data => {
                setResult(
                    (Object.entries(data)
                        .map(([url, score]) => ({url: url, score: score})) as Result[])
                        .sort((a, b) => (a.score < b.score) ? 1 : -1)
                        .map(value => ({ ...value, score: Math.floor(value.score)}))
                )
            })
    }

    const handleKeypress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            queryServer()
        }
    }

    return (
        <div className={styles.searchbar}>
            <Input onChange={handleChange} onKeyPress={handleKeypress} clearable icon={<Search />} placeholder="Search" width={"100%"} height={1} />
            <Button onClick={queryServer} style={{border: 'none'}} iconRight={<CornerDownLeft />} px={"0.5"} width={"auto"} height={"36px"} />
        </div>
    )
}