Proiect realizat la disciplina Retele de calculatoare - proiect, 2023-2024.
Proiect care include 3 scripuri Python:

1. server.py - este un script ce va monitoriza una sau mai multe resurse ale sistemului de calcul (încărcare procesor, memorie utilizată, temperaturi etc.), numărul și tipul resurselor fiind selectabil la nivel de interfață. Scriptul va expune resursele monitorizate sub formă de servicii DNS-SD (SRV) asociate cu un nume (hostname) configurat la nivel de interfață (PTR). Valorile monitorizate vor fi expuse prin intermediul unor înregistrări TXT.
2. client.py - este scriptul care se va conecta la server si va primi prin intermediul mDNS ceea ce s-a trimis de catre server.
3. descoperire_servicii.py - este un script ce realizează descoperirea serviciilor disponibile în rețeaua locală. La selectarea unei intrări se afișează adresa IP a mașinii pe care rulează acea instanță, respectiv valoarea resursei.


Captura din client.py
![Alt text](https://i.imgur.com/i1ZyRfN.png)

Captura din descoperire_servicii.py
![Alt text](https://i.imgur.com/OR584EJ.png)
