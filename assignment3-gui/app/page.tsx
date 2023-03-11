'use client'

import SearchBar from "./SearchBar";
import styles from './page.module.css'
import {Text} from '@geist-ui/core'
import ResultsTable from "./ResultsTable";
import {useState} from "react";

export type Result = {
    url: string
    score: number
}

export default function Home() {
    // Store results as a React state
    const [results, setResults] = useState<Array<Result>>([])

    return (
        <main className={styles.main}>
            <div className={styles.title}>
                <Text  h1>ICSearch</Text>
            </div>
            <div className={styles.search}>
                <SearchBar results={results} setResult={setResults}/>
                {/*Add space in between*/}
                <div style={{height: '2rem'}}/>
                <ResultsTable results={results}/>
            </div>
        </main>
    )
}
