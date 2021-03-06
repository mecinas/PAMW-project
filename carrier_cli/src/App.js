import React, { PureComponent } from 'react';
import axios from 'axios';
import DropdownEl from './elements/DropdownEl';
import { Table } from 'reactstrap';
import jwt from 'jsonwebtoken';

export default class App extends PureComponent {
  is_authorized = true
  state = {
    "all_packages": []
  }
  createToken() {
    let key = process.env.REACT_APP_JWT_SECRET;
    let payload = {
      "login": global.account
    }
    let token = jwt.sign(payload, key)
    return token
  }
  token = this.createToken()
  server_error = false

  downloadPackages() {
    let path = 'https://murmuring-springs-10121.herokuapp.com/root/carrier/dashboard'
    axios.get(path, {
      headers: {
        "auth_cookie": this.token
      }
    }).catch(function (error) {
      if (error.response) {
        this.server_error = true
      }
    }).then(resp => {
      if (resp.data.data.is_authorized) {
        this.setState({ "all_packages": resp.data.data.all_packages })
      }
      else
        this.is_authorized = false
    })
    this.server_error = false
  }

  send_post_request = (state, index_of_row, username) => {
    let path = 'https://murmuring-springs-10121.herokuapp.com/root/carrier/dashboard'
    axios.put(path, null, {
      params: {
        "user": username,
        "index_of_row": index_of_row,
        "state": state
      },
      headers: {
        "auth_cookie": this.token
      }
    }).catch(function (error) {
      if (error.response) {
        this.server_error = true
      }
    });
    this.server_error = false
  }

  render() {
    if (!this.is_authorized) {
      return 'Błędna autoryzacja, 401'
    }
    else {
      this.downloadPackages()
      if (this.server_error) {
        return 'Problem w połączeniu w serwerem, 500'
      }
      let start_packages = this.state.all_packages
      let packages = start_packages.map((single_package) => {
        return (
          <tr key={single_package.id}>
            <td>{single_package.sender_name}</td>
            <td>{single_package.adressee_name}</td>
            <td>{single_package.storeroom_id}</td>
            <td>{single_package.size}</td>
            <td>{single_package.state}</td>
            <td>
              <DropdownEl send_post_request={this.send_post_request} index_of_row={single_package.id}
                username={single_package.sender_name} />
            </td>
          </tr>
        )
      });

      if (global.auth) {
        return (
          <div className="content_container">
            <Table>
              <thead>
                <tr>
                  <th>Nazwa nadawcy</th>
                  <th>Nazwa adresata</th>
                  <th>Skrytka docelowa</th>
                  <th>Rozmiar paczki</th>
                  <th>Stan</th>
                  <th>Zmień stan</th>
                </tr>
              </thead>
              <tbody>
                {packages}
              </tbody>
            </Table>
          </div>
        );
      }else {
        return (
          <div>
            Niezalogowany
          </div>
        )
      }
    }
  }
}