import {List, Frame, Toast, DataTable, DatePicker, Checkbox ,Select, AppProvider, Card,TextField, Button, TextStyle, EmptyState, Form, FormLayout, Layout, Page } from '@shopify/polaris';
import React, {Component, useState, useCallback} from 'react';
import ReactDOM from "react-dom";
import '@shopify/polaris/dist/styles.css';
import translations from '@shopify/polaris/locales/en.json';


class Main extends Component{

    constructor(props) {
        super(props);

    }

    render() {

        return (
            <AppProvider i18n={translations}>
                <Frame>
                    <Page title="Plans">
                        <Layout>
                            <Layout.Section oneThird style={{ height: '100%' }}>
                                <Card style={{ height: '100%' }}>
                                    <Card.Section >
                                        <p>dsadsadsa</p>
                                    </Card.Section>
                                </Card>
                            </Layout.Section>
                            <Layout.Section oneThird style={{ height: '100%' }}>
                                <Card style={{ height: '100%' }}>
                                    <Card.Section >
                                        <p>dsadsadsa</p>
                                    </Card.Section>
                                </Card>
                            </Layout.Section>
                            <Layout.Section oneThird style={{ height: '100%' }}>
                                <Card style={{ height: '100%' }}>
                                    <Card.Section >
                                    <p>dsadsadsa</p>
                                    </Card.Section>
                                </Card>
                            </Layout.Section>
                        </Layout>
                    </Page>
                </Frame>
            </AppProvider>
        )
    }
}

export default Main;

// const wrapper = document.getElementById("root");
// wrapper ? ReactDOM.render(<Main />, wrapper) : false;





