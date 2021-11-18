import {AppProvider, Button, Card,TextField, TextStyle, EmptyState, Form, FormLayout, Layout, Page } from '@shopify/polaris';
import React, {Component, useState, useCallback} from 'react';
import ReactDOM from "react-dom";
import '@shopify/polaris/dist/styles.css';
import translations from '@shopify/polaris/locales/en.json';


class SettingButton extends Component{
    render(){
        return(
            <Form >
                <Button submit>Setting</Button>
            </Form>
        )
    }
}

class NameForm extends Component{

    constructor(props) {
        super(props);
        this.state = {name: ''};
        this.handleNameChange = this.handleNameChange.bind(this)
        this.handleSubmit = this.handleSubmit.bind(this)
    }

    handleNameChange(event){
        this.setState({name: event.target.value});
    }

    handleSubmit(event){
        alert("Name: " + this.state.name)
        event.preventDefault();
    }

    render(){
        return(
            <Form onSubmit={this.handleSubmit}>
                <FormLayout>
                    <TextField
                    value={this.state.name}
                    onChange={this.handleNameChange}
                    label="Name"
                    helpText={<span>Polaris</span>}
                    />
                    <Button submit>Submit</Button>
                </FormLayout>
            </Form>
        )
    }
}

function NameFormExample(){
    const [name, setName] = useState('');

    const handleSubmit = useCallback((_event) => {
    alert(" Name: "+ name)
    }, [name]);

    const handleNameChange = useCallback((value) => setName(value), []);

    return (
    <Form onSubmit={handleSubmit}>
      <FormLayout>
        <TextField
          value={name}
          onChange={handleNameChange}
          label="Name"
          type="text"
          helpText={
            <span>
              Polaris
            </span>
          }
        />

        <Button submit>Submit</Button>
      </FormLayout>
    </Form>
  );

}



class Hello extends Component {

    constructor(props){
        super(props);
        this.state = {
            message:'Welcome to code 101'
        };
    }

    render() {
        return (
            <AppProvider i18n={translations}>
                <Page>
                    <Layout>
                        <Layout.Section oneThird>
                            <SettingButton />
                        </Layout.Section>
                        <Layout.Section oneThird>
                            <Card title="General Settings" sectioned>
                              <NameFormExample />
                            </Card>
                            <Card title="Export To Xero" sectioned>
                              <NameFormExample />
                            </Card>
                            <Card title="History" sectioned>
                              <NameFormExample />
                            </Card>
                            <Card title="Plans" sectioned>
                              <NameFormExample />
                            </Card>
                            <Card title="Disconnect From Xero" sectioned>
                              <NameFormExample />
                            </Card>
                        </Layout.Section>

                    </Layout>
                </Page>
            </AppProvider>
        )
    }

}

const Index = () => (
    <Hello />
);

export default Hello;

// const wrapper = document.getElementById("container12");
// wrapper ? ReactDOM.render(<Hello />, wrapper) : false;



class PlanForm extends Component{

    constructor(props) {
        super(props);
        this.state = {
        plans: AppConfig.plans.map((plan) =>(
            <Layout.Section oneThird>
                <div className="card">
                    <Card title={plan.plan_name}
                    sectioned>
                        if(plan.plan_cost > 0){
                            <p>
                        <b>Free</b>
                        </p>
                    }else{
                        <p>
                        <b>{plan.plan_cost}/month</b>
                        </p>
                    }
                        <p>Sync Customers, Products, Orders to Xero</p>
                        <p>Manually Sync in date range</p>
                        <p>Automatic Updates every 24 hours</p>
                        <p>Account Mapping</p>
                        <p>Synchronization History</p>
                        <p>100 Orders/month</p>
                    </Card>
                </div>
            </Layout.Section>
          )
        )
        };
    }

    render() {
        return (
            <Layout>
                <Layout.Section oneThird>
                    <div className="card">
                        <div className="card-body d-flex flex-column">
                            <Card title="Plan name1"
                                  sectioned>
                                <p>
                                    <b>Free</b>
                                </p>
                                <p>Sync Customers, Products, Orders to Xero</p>
                                <p>Manually Sync in date range</p>
                                <p>Automatic Updates every 24 hours</p>
                                <p>Account Mapping</p>
                                <p>Synchronization History</p>
                                <p>100 Orders/month</p>
                            </Card>
                        </div>
                    </div>
                </Layout.Section>
                <Layout.Section oneThird>
                    <div className="card">
                        <div className="card-body d-flex flex-column">
                            <Card title="Plan name2"
                                  sectioned>
                                <Form>
                                    <p>
                                        <b>$19.99/month</b>
                                    </p>
                                    <p>All Essential Features</p>
                                    <p>Automatic Updates every 12 hours</p>
                                    <p>Sync Gift Cards, Refunds to Xero</p>
                                    <p>800 Orders/month</p>
                                    <div style={{textAlign: 'center', marginTop: '10px'}}>
                                        <Button primary>Sign Up</Button>

                                    </div>
                                </Form>
                            </Card>
                        </div>
                    </div>

                </Layout.Section>
                <Layout.Section oneThird>
                    <div className="card">
                        <div className="card-body d-flex flex-column">
                            <Card title="Plan name3"
                                  sectioned>
                                <Form>
                                    <p>
                                        <b>$29.99/month</b>
                                    </p>
                                    <p>All Standard Features</p>
                                    <p>Automatic Updates every 3 hours</p>
                                    <p>Unlimited Orders per month</p>
                                    <div style={{textAlign: 'center', marginTop: '10px'}}>
                                        <Button primary>Sign Up</Button>
                                    </div>
                                </Form>
                            </Card>
                        </div>
                    </div>
                </Layout.Section>
            </Layout>
        )
    }
}

