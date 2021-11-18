import "./test.css";
import React, {Component} from "react";
import ReactDOM from 'react-dom';
import {
    Link,
    List,
    Frame,
    Toast,
    DataTable,
    DatePicker,
    Checkbox,
    Select,
    AppProvider,
    Card,
    Button,
    TextStyle,
    Form,
    FormLayout,
    Layout,
    Page
} from '@shopify/polaris';
import '@shopify/polaris/build/esm/styles.css';
import image from './shopify.jpg';


class Xero extends Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <AppProvider>
                <Frame>
                    <Page>
                        <div className="test_div">
                            <img className="test_image" src={image} alt="Connect to Xero"/>
                            <div style={{fontSize: '18px',}}>
                                <b>Welcome to Xero Integration</b>
                            </div>

                        </div>
                        <div className="test_button">
                            <Button onClick={event => window.top.location.href = "/xero_connect"} primary>Connect To
                                Xero Accounting</Button>
                        </div>
                        <div className="test_description">
                            <ol>
                                <li><Link onClick={event => window.top.location.href = "https://www.xero.com/signup/"}>Signup
                                    an account</Link> if you haven't already
                                </li>
                                <li>Click "Connect to Xero"</li>
                                <li>Login to Xero if you haven't already</li>
                                <li>Click "Accept" to start connecting to the application</li>
                                <li>Start Exporting data to your Xero Account</li>
                            </ol>
                        </div>
                    </Page>
                </Frame>
            </AppProvider>
        )
    }
}

export default Xero;

if (typeof document != "undefined") {
    const wrapper = document.getElementById("xero_form_login");
    wrapper ? ReactDOM.render(<Xero/>, wrapper) : false;
}

