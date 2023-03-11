'use client'
import {Link, Table} from '@geist-ui/core'
import {TableColumnRender} from "@geist-ui/core/dist/table";
import {Result} from "@/app/page";

const renderHandler: TableColumnRender<Result> = (value, rowData, index) => {
    return <Link underline href={rowData.url}> {rowData.url} </Link>
}

interface ResultProps {
    results: Result[]
}

export default function ResultsTable(props: ResultProps) {
    return props.results.length > 0 ? (
        // @ts-ignore
        <Table<Result> data={props.results} scale={0.5} >
            <Table.Column<Result> prop="url" label="url" width={400} render={renderHandler} />
            <Table.Column<Result> prop="score" label="score" width={1} />
        </Table>
    ) : <></>
}