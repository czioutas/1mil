const { PrismaClient } = require('@prisma/client')
const prisma = new PrismaClient()

async function main() {
  // Create organizations
  const organizations = await Promise.all([
    prisma.organization.upsert({
      where: { id: 1 },
      update: {},
      create: {
        name: 'Acme Corp',
      },
    }),
    prisma.organization.upsert({
      where: { id: 2 },
      update: {},
      create: {
        name: 'EcoTech Solutions',
      },
    }),
    prisma.organization.upsert({
      where: { id: 3 },
      update: {},
      create: {
        name: 'Green Energy Ltd',
      },
    }),
  ])

  // Create sample emissions for each organization
  // for (const org of organizations) {
  //   // Create emissions for the last 30 days
  //   const now = new Date()
  //   for (let i = 0; i < 30; i++) {
  //     const date = new Date(now)
  //     date.setDate(date.getDate() - i)
      
  //     await prisma.emission.create({
  //       data: {
  //         organizationId: org.id,
  //         value: Math.random() * 100, // Random emission value between 0 and 100
  //         timestamp: date,
  //       },
  //     })
  //   }
  // }

  console.log('Seeding completed!')
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })